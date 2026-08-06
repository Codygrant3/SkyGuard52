#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardYak52Aircraft.generated.h"

class UAudioComponent;
class UBoxComponent;
class UPrimitiveComponent;
class USceneComponent;
class UStaticMesh;
class UStaticMeshComponent;

UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardYak52Aircraft : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardYak52Aircraft();

	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Aircraft")
	void SetEnginePower(float NormalizedPower);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Aircraft")
	void IssuePilotCommand(ESkyguardPilotCommand Command);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Aircraft")
	void SetRearCanopyOpen(bool bOpen);

	UFUNCTION(BlueprintPure, Category="Skyguard|Aircraft")
	USceneComponent* GetRearGunnerMount() const { return RearGunnerMount; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Aircraft")
	USceneComponent* GetRearEyeMount() const { return RearEyeMount; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Aircraft")
	USceneComponent* GetRearWeaponMount() const { return RearWeaponMount; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Aircraft")
	float GetPropellerRPM() const { return CurrentPropellerRPM; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Aircraft")
	ESkyguardPilotCommand GetPilotCommand() const { return CurrentPilotCommand; }

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<USceneComponent> AircraftRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UStaticMeshComponent> Airframe;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UStaticMeshComponent> Wings;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UStaticMeshComponent> EngineCowling;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UStaticMeshComponent> HorizontalTail;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UStaticMeshComponent> VerticalTail;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UStaticMeshComponent> CockpitTub;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UStaticMeshComponent> RearPanel;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UStaticMeshComponent> FrontCanopyGlass;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UStaticMeshComponent> RearCanopyGlass;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UStaticMeshComponent> PropellerHub;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UStaticMeshComponent> PropellerBlade;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<USceneComponent> RearGunnerMount;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<USceneComponent> RearEyeMount;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<USceneComponent> RearWeaponMount;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UBoxComponent> PilotProtection;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Aircraft")
	TObjectPtr<UBoxComponent> CockpitProtection;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Aircraft", meta=(ClampMin="900.0", ClampMax="3200.0"))
	float MinimumFlightRPM = 1800.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Aircraft", meta=(ClampMin="900.0", ClampMax="3600.0"))
	float MaximumFlightRPM = 2800.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Aircraft", meta=(ClampMin="0.0", ClampMax="1.0"))
	float EnginePower = 0.82f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Aircraft")
	float PilotResponseDegreesPerSecond = 26.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Aircraft")
	float RearCanopyTravelCentimeters = 82.f;

private:
	void ConfigureVisual(UStaticMeshComponent* Component, const TCHAR* AssetPath);
	FRotator GetCommandAttitude() const;

	float CurrentPropellerRPM = 0.f;
	float RearCanopyAlpha = 1.f;
	bool bRearCanopyOpen = true;
	ESkyguardPilotCommand CurrentPilotCommand = ESkyguardPilotCommand::Pursuit;
	FVector RearCanopyClosedLocation = FVector::ZeroVector;
};
