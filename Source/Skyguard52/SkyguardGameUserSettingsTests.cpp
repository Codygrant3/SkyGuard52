#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGameUserSettings.h"
#include "HAL/FileManager.h"
#include "Misc/AutomationTest.h"
#include "Misc/Paths.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGameUserSettingsValidationTest,
	"Skyguard52.Settings.ValidationClampsAndRestoresDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGameUserSettingsValidationTest::RunTest(const FString& Parameters)
{
	USkyguardGameUserSettings* Settings =
		NewObject<USkyguardGameUserSettings>(GetTransientPackage());
	TestNotNull(TEXT("Skyguard settings object can be created"), Settings);
	if (!Settings)
	{
		return false;
	}

	Settings->SetMasterVolume(5.f);
	Settings->SetMouseSensitivity(-20.f);
	Settings->SetCameraShakeScale(2.f);
	TestEqual(TEXT("Master volume clamps to one"), Settings->GetMasterVolume(), 1.f);
	TestEqual(TEXT("Mouse sensitivity clamps to safe minimum"), Settings->GetMouseSensitivity(), 0.005f);
	TestEqual(TEXT("Camera shake clamps to one"), Settings->GetCameraShakeScale(), 1.f);

	Settings->SetMasterVolume(-1.f);
	Settings->SetMouseSensitivity(10.f);
	Settings->SetCameraShakeScale(-1.f);
	Settings->SetInvertVerticalLook(true);
	TestEqual(TEXT("Master volume clamps to zero"), Settings->GetMasterVolume(), 0.f);
	TestEqual(TEXT("Mouse sensitivity clamps to safe maximum"), Settings->GetMouseSensitivity(), 0.5f);
	TestEqual(TEXT("Camera shake clamps to zero"), Settings->GetCameraShakeScale(), 0.f);
	TestTrue(TEXT("Vertical inversion is retained"), Settings->GetInvertVerticalLook());

	Settings->SetToDefaults();
	TestEqual(TEXT("Default master volume is full"), Settings->GetMasterVolume(), 1.f);
	TestEqual(TEXT("Default sensitivity matches authored baseline"), Settings->GetMouseSensitivity(), 0.07f);
	TestEqual(TEXT("Default camera shake is full"), Settings->GetCameraShakeScale(), 1.f);
	TestTrue(TEXT("Vertical look is inverted by default"), Settings->GetInvertVerticalLook());
	TestEqual(TEXT("Default frame limit is 120 fps"), Settings->GetFrameRateLimit(), 120.f);
	TestEqual(TEXT("Default scalability is Epic"), Settings->GetOverallScalabilityLevel(), 3);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGameUserSettingsConfigRoundTripTest,
	"Skyguard52.Settings.ConfigRoundTripPersistsProjectPreferences",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGameUserSettingsConfigRoundTripTest::RunTest(const FString& Parameters)
{
	const FString TempIni = FPaths::CreateTempFilename(
		*FPaths::ProjectSavedDir(),
		TEXT("SkyguardSettingsAutomation_"),
		TEXT(".ini"));

	USkyguardGameUserSettings* Source =
		NewObject<USkyguardGameUserSettings>(GetTransientPackage());
	Source->SetMasterVolume(0.35f);
	Source->SetMouseSensitivity(0.12f);
	Source->SetInvertVerticalLook(true);
	Source->SetCameraShakeScale(0.4f);
	Source->SaveConfig(CPF_Config, *TempIni);

	USkyguardGameUserSettings* Restored =
		NewObject<USkyguardGameUserSettings>(GetTransientPackage());
	Restored->LoadConfig(nullptr, *TempIni);
	Restored->ValidateSettings();
	TestEqual(TEXT("Master volume survives config round trip"), Restored->GetMasterVolume(), 0.35f);
	TestEqual(TEXT("Mouse sensitivity survives config round trip"), Restored->GetMouseSensitivity(), 0.12f);
	TestTrue(TEXT("Vertical inversion survives config round trip"), Restored->GetInvertVerticalLook());
	TestEqual(TEXT("Camera shake scale survives config round trip"), Restored->GetCameraShakeScale(), 0.4f);

	TestTrue(
		TEXT("Temporary settings receipt is deleted"),
		IFileManager::Get().Delete(*TempIni, false, true));
	return true;
}

#endif
