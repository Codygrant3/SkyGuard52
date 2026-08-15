#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "SkyguardPauseSettingsWidget.generated.h"

class UButton;
class UCheckBox;
class USlider;

/** Blueprintable pause/settings surface with a complete C++ runtime fallback. */
UCLASS(Blueprintable, BlueprintType)
class SKYGUARD52_API USkyguardPauseSettingsWidget : public UUserWidget
{
	GENERATED_BODY()

protected:
	virtual void NativeConstruct() override;

private:
	UPROPERTY(Transient)
	TObjectPtr<USlider> MasterVolumeSlider;

	UPROPERTY(Transient)
	TObjectPtr<USlider> MouseSensitivitySlider;

	UPROPERTY(Transient)
	TObjectPtr<UCheckBox> InvertLookCheckBox;

	UPROPERTY(Transient)
	TObjectPtr<USlider> CameraShakeSlider;

	UPROPERTY(Transient)
	TObjectPtr<UButton> ApplyButton;

	UPROPERTY(Transient)
	TObjectPtr<UButton> ResumeButton;

	UFUNCTION()
	void HandleMasterVolumeChanged(float Value);

	UFUNCTION()
	void HandleMouseSensitivityChanged(float Value);

	UFUNCTION()
	void HandleInvertLookChanged(bool bChecked);

	UFUNCTION()
	void HandleCameraShakeChanged(float Value);

	UFUNCTION()
	void HandleApplyClicked();

	UFUNCTION()
	void HandleResumeClicked();
};
