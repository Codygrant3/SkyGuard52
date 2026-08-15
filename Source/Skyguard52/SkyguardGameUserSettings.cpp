#include "SkyguardGameUserSettings.h"

#include "Engine/Engine.h"
#include "Misc/App.h"

FSkyguardUserSettingsApplied USkyguardGameUserSettings::OnSettingsApplied;

USkyguardGameUserSettings::USkyguardGameUserSettings()
{
	SetToDefaults();
}

USkyguardGameUserSettings* USkyguardGameUserSettings::GetSkyguardGameUserSettings()
{
	return GEngine
		? Cast<USkyguardGameUserSettings>(GEngine->GetGameUserSettings())
		: nullptr;
}

void USkyguardGameUserSettings::SetMasterVolume(const float Value)
{
	MasterVolume = FMath::Clamp(Value, 0.f, 1.f);
}

void USkyguardGameUserSettings::SetMouseSensitivity(const float Value)
{
	MouseSensitivity = FMath::Clamp(Value, 0.005f, 0.5f);
}

void USkyguardGameUserSettings::SetCameraShakeScale(const float Value)
{
	CameraShakeScale = FMath::Clamp(Value, 0.f, 1.f);
}

void USkyguardGameUserSettings::ValidateSettings()
{
	Super::ValidateSettings();
	SetMasterVolume(MasterVolume);
	SetMouseSensitivity(MouseSensitivity);
	SetCameraShakeScale(CameraShakeScale);
}

void USkyguardGameUserSettings::SetToDefaults()
{
	Super::SetToDefaults();
	MasterVolume = 1.f;
	MouseSensitivity = 0.07f;
	bInvertVerticalLook = true;
	CameraShakeScale = 1.f;
	SetVSyncEnabled(false);
	SetFrameRateLimit(120.f);
	SetOverallScalabilityLevel(3);
}

void USkyguardGameUserSettings::ApplySettings(
	const bool bCheckForCommandLineOverrides)
{
	ValidateSettings();
	Super::ApplySettings(bCheckForCommandLineOverrides);
	FApp::SetVolumeMultiplier(MasterVolume);
	OnSettingsApplied.Broadcast(*this);
}

void USkyguardGameUserSettings::ApplyAndSaveSettings(
	const bool bCheckForCommandLineOverrides)
{
	ApplySettings(bCheckForCommandLineOverrides);
	SaveSettings();
}
