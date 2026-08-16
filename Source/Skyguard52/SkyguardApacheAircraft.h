#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardApacheAircraft.generated.h"

class UBoxComponent;
class USceneComponent;
class UStaticMeshComponent;

/**
 * Arcade AH-64-style gunship. Public HowStuffWorks layout only:
 * front CPG, aft pilot, TADS, M230, stub-wing Hydra/Hellfire, engines,
 * Longbow-style dome. Proxy primitives — silhouette, not a photoreal kit.
 */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardApacheAircraft : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardApacheAircraft();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	USceneComponent* GetGunnerMount() const { return GunnerMount; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	USceneComponent* GetEyeMount() const { return EyeMount; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	USceneComponent* GetWeaponMount() const { return WeaponMount; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	USceneComponent* GetChinTurret() const { return ChinTurret; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	USceneComponent* GetPilotMount() const { return PilotMount; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	USceneComponent* GetSensorTurret() const { return SensorTurret; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	FVector GetChinMuzzleLocation() const;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void AimChinTurret(const FRotator& WorldAim);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void SetRotorPower(float NormalizedPower);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void IssuePilotCommand(ESkyguardPilotCommand Command);

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	ESkyguardPilotCommand GetPilotCommand() const { return CurrentPilotCommand; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	int32 GetPilotConfirmationsIssued() const { return PilotConfirmationsIssued; }

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void SetOrbitFocus(const FVector& WorldLocation);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void FaceWorldLocation(const FVector& WorldLocation);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void SetSensorView(bool bInSensor);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void SetFirstPersonInterior(bool bInterior);

	/** W/S collective, A/D pivot, arrows point the nose. */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache")
	void SetDirectFlightInput(
		float Collective,
		float Yaw,
		float CyclicPitch,
		float CyclicRoll);

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	float GetForwardSpeed() const { return ForwardSpeed; }

	UFUNCTION(BlueprintCallable, Category="Skyguard|Apache|Damage")
	void ApplyDamage(float Amount);

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache|Damage")
	float GetDamageFraction() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
	float GetRotorRPM() const { return CurrentRotorRPM; }

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache|Damage",
		meta=(ClampMin="1.0"))
	float MaxIntegrity = 140.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache|Damage")
	float CurrentIntegrity = 140.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache|Damage")
	TObjectPtr<UBoxComponent> HullCollider;

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<USceneComponent> AircraftRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> SilhouetteMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> Fuselage;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> Nose;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> Canopy;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> TailBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> VerticalTail;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> StubWingLeft;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> StubWingRight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> RotorMast;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> MainRotor;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> TailRotor;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<USceneComponent> ChinTurret;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> ChinHousing;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> ChinBarrel;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<USceneComponent> SensorTurret;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> SensorBall;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> NightVisionTurret;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> PilotCanopy;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> EngineLeft;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> EngineRight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> RadarDome;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> MainRotorCross;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> HorizontalTail;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> GearNose;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> GearLeft;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> GearRight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> PylonLeft;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> PylonRight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> HydraLeft;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> HydraRight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> HellfireLeft;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<UStaticMeshComponent> HellfireRight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<USceneComponent> GunnerMount;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<USceneComponent> PilotMount;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<USceneComponent> EyeMount;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
	TObjectPtr<USceneComponent> WeaponMount;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache",
		meta=(ClampMin="0.0", ClampMax="1.0"))
	float RotorPower = 0.88f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Apache")
	float HoverBobCentimeters = 10.f;

private:
	UStaticMeshComponent* CreateVisual(const TCHAR* Name, USceneComponent* Parent);
	void BindPrimitive(
		UStaticMeshComponent* Component,
		UStaticMesh* Mesh,
		const FVector& Location,
		const FRotator& Rotation,
		const FVector& Scale,
		const FLinearColor& Color);
	void Tint(UStaticMeshComponent* Component, const FLinearColor& Color) const;
	void ApplyPendingTints();
	void OpenCockpitView();
	void BindSilhouetteMesh();
	void SetProxyKitHidden(bool bHideKit);

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInterface> ShapeMaterial;
	void UpdatePilotMotion(float DeltaSeconds);
	void UpdateDirectFlight(float DeltaSeconds);
	void PollPilotCommandInput();
	FRotator GetCommandAttitude() const;
	bool IsActionJustPressed(const FName ActionName) const;

	TMap<TObjectPtr<UStaticMeshComponent>, FLinearColor> PendingTint;
	float CurrentRotorRPM = 0.f;
	float HoverSeconds = 0.f;
	FVector HoverBaseLocation = FVector::ZeroVector;
	FVector OrbitCenter = FVector::ZeroVector;
	FVector FaceTargetLocation = FVector::ZeroVector;
	float OrbitRadius = 2200.f;
	float OrbitAngleDegrees = 180.f;
	bool bSensorView = false;
	bool bHasDirectFlight = false;
	float CollectiveInput = 0.f;
	float YawInput = 0.f;
	float CyclicPitchInput = 0.f;
	float CyclicRollInput = 0.f;
	float ForwardSpeed = 900.f;
	float AirYawDegrees = 0.f;
	float AirPitchDegrees = 0.f;
	float AirRollDegrees = 0.f;
	ESkyguardPilotCommand CurrentPilotCommand = ESkyguardPilotCommand::Pursuit;
	int32 PilotConfirmationsIssued = 0;
};
