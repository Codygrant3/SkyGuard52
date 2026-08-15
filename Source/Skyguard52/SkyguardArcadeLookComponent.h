#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardArcadeLookComponent.generated.h"

class UCameraComponent;

/**
 * First-person dusk-combat grade. Not a photoreal calibration.
 * Makes the existing proxy world read as an intentional night intercept.
 */
UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardArcadeLookComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	USkyguardArcadeLookComponent();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Arcade")
	void ApplyToCamera(UCameraComponent* Camera);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Arcade")
	void ApplyHelmetSight(UCameraComponent* Camera);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Arcade")
	void ApplyTargetingSensor(UCameraComponent* Camera);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Arcade")
	void ApplyThermalSensor(UCameraComponent* Camera);

	/** Idempotent dusk fog + unbound grade for the current world. */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Arcade",
		meta=(WorldContext="WorldContextObject"))
	static void ApplyWorldMood(UObject* WorldContextObject);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Arcade",
		meta=(WorldContext="WorldContextObject"))
	static void ApplyWorldMoodForWeather(
		UObject* WorldContextObject,
		ESkyguardMissionWeather Weather);

	UFUNCTION(BlueprintPure, Category="Skyguard|Arcade")
	bool IsEnabled() const { return bEnabled; }

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Arcade")
	bool bEnabled = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Arcade")
	float Contrast = 1.18f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Arcade")
	float Saturation = 1.12f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Arcade")
	float Gain = 1.08f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Arcade")
	float Gamma = 0.92f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Arcade")
	float BloomIntensity = 0.55f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Arcade")
	float Vignette = 0.42f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Arcade")
	float Grain = 0.08f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Arcade")
	float ChromaticAberration = 0.35f;
};
