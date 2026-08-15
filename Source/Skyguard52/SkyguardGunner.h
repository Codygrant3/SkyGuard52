#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "SkyguardBossTypes.h"
#include "SkyguardCpgHud.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardGunner.generated.h"

class ASkyguardApacheAircraft;
class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;
class UInputComponent;
class USceneComponent;
class UCameraShakeBase;
class USkyguardGameUserSettings;
class UMaterialInterface;
class UStaticMesh;
class UTextRenderComponent;
class UFont;
class USkyguardCpgSightHud;

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
	 * Prefers the attached Apache, then a Yak fallback.
	 */
	UFUNCTION(BlueprintPure, Category="Skyguard|Combat|Sortie")
	float GetSortieAircraftDamageFraction() const;

	void RecordRifleShot();
	void RecordRifleHit();
	void RecordIglaShot();
	void RecordIglaHit();

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	ESkyguardGunshipWeapon GetSelectedGunshipWeapon() const
	{
		return SelectedGunshipWeapon;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	int32 GetRocketAmmo() const { return RocketAmmo; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	int32 GetGuidedAmmo() const { return GuidedAmmo; }

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void SelectGunshipWeapon(ESkyguardGunshipWeapon Weapon);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void ReloadSelectedWeapon();

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	bool IsReloading() const { return bReloading; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	int32 GetCannonMagazine() const { return CannonMagazine; }

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void ApplyLoadout(ESkyguardLoadout Loadout);

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	ESkyguardLoadout GetActiveLoadout() const { return ActiveLoadout; }

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void ToggleThermal();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void PopFlares();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void NotifyMissileInbound();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	bool TryDefeatInboundWithFlares();

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	bool IsThermalEnabled() const { return bThermalEnabled; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	int32 GetFlareCount() const { return FlareCount; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	bool IsMissileInbound() const { return bMissileInbound; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	float GetLockProgress() const { return IglaLockProgress; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	bool IsApacheGunnerMode() const { return bApacheGunnerMode; }

	FSkyguardCpgHudSnapshot BuildCpgHudSnapshot() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	bool IsCpgSightActive() const { return bApacheGunnerMode && bADS; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	AActor* GetCpgLockTarget() const { return IglaTarget.Get(); }

	void CollectCpgContactMarks(TArray<FSkyguardCpgContactMark>& OutMarks) const;

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
	TObjectPtr<USceneComponent> CpgStation;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgCockpit;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgSeatBack;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgSeatPan;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgKneeLeft;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgKneeRight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgCanopyBow;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgDash;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgTedac;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgMpdLeft;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgMpdRight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgEufd;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgTedacBezel;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgReticleH;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgReticleV;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgGripLeft;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgGripRight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgConsoleRight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgRailLeft;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> CpgRailRight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UTextRenderComponent> CpgTedacText;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UTextRenderComponent> CpgMpdLeftText;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UTextRenderComponent> CpgMpdRightText;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UTextRenderComponent> CpgEufdText;

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

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	ESkyguardGunshipWeapon SelectedGunshipWeapon = ESkyguardGunshipWeapon::Cannon;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	float RocketSalvoSeconds = 1.15f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	float RocketDamage = 72.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	int32 RocketsPerSalvo = 6;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	float RocketSpreadDegrees = 3.6f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	int32 CannonMagazineSize = 30;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	int32 CannonMagazine = 30;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	int32 CannonReserve = 300;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	int32 RocketMagazineSize = 14;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	int32 RocketAmmo = 14;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	int32 RocketReserve = 24;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	int32 GuidedMagazineSize = 2;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	int32 GuidedAmmo = 2;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	int32 GuidedReserve = 6;

	friend class FSkyguardApacheReloadFillsMagazineTest;

	bool bADS = false;
	bool bFireHeld = false;
	bool bIglaMode = false;
	bool bApacheGunnerMode = false;
	float FireCooldown = 0.f;
	float Yaw = 0.f;
	float Pitch = -2.f;
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
	void InputSelectWeapon1();
	void InputSelectWeapon2();
	void InputSelectWeapon3();
	void InputLaunchIglaPressed();
	void InputReloadPressed();
	void InputToggleThermal();
	void InputPopFlares();
	void AdvanceReload(float DeltaSeconds);
	void FinishReload();
	int32 GetSelectedReadyAmmo() const;
	int32 GetSelectedMagazineSize() const;
	void InputPilotCollective(float Value);
	void InputPilotYaw(float Value);
	void InputPilotCyclicPitch(float Value);
	void InputPilotCyclicRoll(float Value);
	void ApplyDirectFlightInput();
	void UpdateSensorAwareness(float DeltaSeconds);
	void ADSPressed();
	void ADSReleased();
	void FirePressed();
	void FireReleased();
	void SwitchWeaponPressed();
	void LaunchIglaPressed();
	void FireShot();
	void FireCannon();
	void FireRockets();
	void FireGuidedMissile();
	void PlayAppliedCameraShake(float IntensityScale = 1.f);
	bool IsRifleDirectionOutsidePilotSafetyArc() const;
	void UpdateADSVisuals(float DeltaSeconds);
	void UpdateIglaLock(float DeltaSeconds);
	void FireIgla();
	void AttachToLivePlatform();
	void ApplyApacheGunnerPresentation();
	void BindCpgVisorPart(
		UStaticMeshComponent* Part,
		const FVector& Location,
		const FVector& Scale,
		const FLinearColor& Color,
		UStaticMesh* ShapeMesh,
		UMaterialInterface* ShapeMat,
		FRotator Rotation = FRotator::ZeroRotator);
	void BindCpgHudText(
		UTextRenderComponent* Text,
		USceneComponent* Parent,
		const FVector& Location,
		const FLinearColor& Color,
		float WorldSize,
		UFont* Font);
	void SetCpgVisorVisible(bool bVisible);
	void SetCpgSightHudVisible(bool bVisible);
	void UpdateCpgHud();
	ASkyguardApacheAircraft* FindAttachedApache() const;
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
	float RocketCooldown = 0.f;
	float SensorTunnelSeconds = 0.f;
	float SensorWarningCooldown = 0.f;
	bool bWasTargetingSensor = false;
	bool bReloading = false;
	float ReloadRemaining = 0.f;
	UPROPERTY(Transient)
	TObjectPtr<USkyguardCpgSightHud> CpgSightHud;

	bool bThermalEnabled = false;
	bool bMissileInbound = false;
	bool bFlarePoppedThisInbound = false;
	int32 FlareCount = 6;
	ESkyguardLoadout ActiveLoadout = ESkyguardLoadout::Balanced;
	float PilotCollectiveAxis = 0.f;
	float PilotYawAxis = 0.f;
	float PilotCyclicPitchAxis = 0.f;
	float PilotCyclicRollAxis = 0.f;
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
	bool bInvertVerticalLookApplied = true;
	bool bUserSettingsBound = false;

	int32 SortieShotsFired = 0;
	int32 SortieHits = 0;
	/** Fallback only when no owning/attached Yak is available. */
	float SortieAircraftDamageFraction = 0.f;
};
