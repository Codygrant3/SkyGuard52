#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameUserSettings.h"
#include "SkyguardGameUserSettings.generated.h"

DECLARE_MULTICAST_DELEGATE_OneParam(
	FSkyguardUserSettingsApplied,
	const class USkyguardGameUserSettings&);

UCLASS(Config = GameUserSettings, ConfigDoNotCheckDefaults, BlueprintType)
class SKYGUARD52_API USkyguardGameUserSettings : public UGameUserSettings
{
	GENERATED_BODY()

public:
	USkyguardGameUserSettings();

	virtual void ApplySettings(bool bCheckForCommandLineOverrides) override;
	virtual void ValidateSettings() override;
	virtual void SetToDefaults() override;

	UFUNCTION(BlueprintPure, Category = "Settings")
	static USkyguardGameUserSettings* GetSkyguardGameUserSettings();

	UFUNCTION(BlueprintCallable, Category = "Settings")
	void ApplyAndSaveSettings(bool bCheckForCommandLineOverrides = true);

	UFUNCTION(BlueprintCallable, Category = "Settings|Audio")
	void SetMasterVolume(float Value);

	UFUNCTION(BlueprintPure, Category = "Settings|Audio")
	float GetMasterVolume() const { return MasterVolume; }

	UFUNCTION(BlueprintCallable, Category = "Settings|Input")
	void SetMouseSensitivity(float Value);

	UFUNCTION(BlueprintPure, Category = "Settings|Input")
	float GetMouseSensitivity() const { return MouseSensitivity; }

	UFUNCTION(BlueprintCallable, Category = "Settings|Input")
	void SetInvertVerticalLook(bool bValue) { bInvertVerticalLook = bValue; }

	UFUNCTION(BlueprintPure, Category = "Settings|Input")
	bool GetInvertVerticalLook() const { return bInvertVerticalLook; }

	UFUNCTION(BlueprintCallable, Category = "Settings|Accessibility")
	void SetCameraShakeScale(float Value);

	UFUNCTION(BlueprintPure, Category = "Settings|Accessibility")
	float GetCameraShakeScale() const { return CameraShakeScale; }

	static FSkyguardUserSettingsApplied OnSettingsApplied;

private:
	UPROPERTY(Config)
	float MasterVolume = 1.f;

	UPROPERTY(Config)
	float MouseSensitivity = 0.07f;

	UPROPERTY(Config)
	bool bInvertVerticalLook = true;

	UPROPERTY(Config)
	float CameraShakeScale = 1.f;
};
