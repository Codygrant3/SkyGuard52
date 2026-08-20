#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGameUserSettings.h"

#include "Misc/App.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGameUserSettingsApplyBroadcastsWithoutSaveTest,
	"Skyguard52.Settings.ApplyBroadcastsWithoutSave",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGameUserSettingsApplyBroadcastsWithoutSaveTest::RunTest(
	const FString& Parameters)
{
	USkyguardGameUserSettings* Settings =
		NewObject<USkyguardGameUserSettings>(GetTransientPackage());
	TestNotNull(TEXT("Skyguard settings object can be created"), Settings);
	if (!Settings)
	{
		return false;
	}

	TestTrue(
		TEXT("NewObject defaults invert vertical look"),
		Settings->GetInvertVerticalLook());

	Settings->SetInvertVerticalLook(false);
	TestFalse(
		TEXT("SetInvertVerticalLook(false) is readable"),
		Settings->GetInvertVerticalLook());
	Settings->SetInvertVerticalLook(true);
	TestTrue(
		TEXT("SetInvertVerticalLook(true) restores inversion"),
		Settings->GetInvertVerticalLook());

	const float PreviousVolumeMultiplier = FApp::GetVolumeMultiplier();
	bool bHandlerRan = false;
	const USkyguardGameUserSettings* SeenSettings = nullptr;
	float SeenMasterVolume = -1.f;
	const FDelegateHandle AppliedHandle =
		USkyguardGameUserSettings::OnSettingsApplied.AddLambda(
			[&](const USkyguardGameUserSettings& Applied)
			{
				bHandlerRan = true;
				SeenSettings = &Applied;
				SeenMasterVolume = Applied.GetMasterVolume();
			});

	Settings->ApplySettings(false);

	TestTrue(TEXT("OnSettingsApplied ran for ApplySettings"), bHandlerRan);
	TestTrue(
		TEXT("OnSettingsApplied saw the NewObject settings"),
		SeenSettings == Settings);
	TestEqual(
		TEXT("OnSettingsApplied saw current master volume"),
		SeenMasterVolume,
		Settings->GetMasterVolume());
	TestEqual(
		TEXT("ApplySettings pushes master volume to FApp"),
		FApp::GetVolumeMultiplier(),
		Settings->GetMasterVolume());

	USkyguardGameUserSettings::OnSettingsApplied.Remove(AppliedHandle);
	FApp::SetVolumeMultiplier(PreviousVolumeMultiplier);
	return true;
}

#endif
