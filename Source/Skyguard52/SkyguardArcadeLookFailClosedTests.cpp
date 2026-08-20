#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardArcadeLookComponent.h"

#include "Camera/CameraComponent.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardArcadeLookTests.cpp.
// Nullptr / disabled fail-closed public API only: NewObject for the
// look component, no Gunner / Yak / Igla / rifle spawn, no world mood
// spawn, no dusk combat grade numbers.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardArcadeLookFailClosedTest,
	"Skyguard52.Arcade.LookFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardArcadeLookFailClosedTest::RunTest(const FString& Parameters)
{
	USkyguardArcadeLookComponent* Look =
		NewObject<USkyguardArcadeLookComponent>(GetTransientPackage());
	TestNotNull(TEXT("NewObject look constructs"), Look);
	if (!Look)
	{
		return false;
	}

	TestTrue(TEXT("NewObject default IsEnabled is true"), Look->IsEnabled());
	TestTrue(TEXT("NewObject default bEnabled is true"), Look->bEnabled);
	TestFalse(
		TEXT("constructor leaves PrimaryComponentTick.bCanEverTick false"),
		Look->PrimaryComponentTick.bCanEverTick);

	Look->ApplyToCamera(nullptr);
	Look->ApplyHelmetSight(nullptr);
	Look->ApplyTargetingSensor(nullptr);
	Look->ApplyThermalSensor(nullptr);
	TestTrue(
		TEXT("null camera applies leave IsEnabled true"),
		Look->IsEnabled());

	USkyguardArcadeLookComponent::ApplyWorldMood(nullptr);
	USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(
		nullptr,
		ESkyguardMissionWeather::Clear);
	USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(
		nullptr,
		ESkyguardMissionWeather::Storm);
	TestTrue(
		TEXT("null world-mood applies are no-ops"),
		Look->IsEnabled());

	UCameraComponent* Camera = NewObject<UCameraComponent>(GetTransientPackage());
	TestNotNull(TEXT("NewObject camera constructs"), Camera);
	if (!Camera)
	{
		return false;
	}

	const float DefaultBlendWeight = Camera->PostProcessBlendWeight;
	const FPostProcessSettings& Settings = Camera->PostProcessSettings;
	TestFalse(
		TEXT("camera default has no helmet fringe override"),
		Settings.bOverride_SceneFringeIntensity);
	TestFalse(
		TEXT("camera default has no helmet vignette override"),
		Settings.bOverride_VignetteIntensity);
	TestFalse(
		TEXT("camera default has no color-gain override"),
		Settings.bOverride_ColorGain);

	Look->bEnabled = false;
	TestFalse(TEXT("IsEnabled follows bEnabled false"), Look->IsEnabled());

	Look->ApplyToCamera(Camera);
	Look->ApplyHelmetSight(Camera);
	Look->ApplyTargetingSensor(Camera);
	Look->ApplyThermalSensor(Camera);

	TestEqual(
		TEXT("disabled applies leave PostProcessBlendWeight at camera default"),
		Camera->PostProcessBlendWeight,
		DefaultBlendWeight);
	TestFalse(
		TEXT("disabled applies do not set helmet fringe"),
		Settings.bOverride_SceneFringeIntensity);
	TestFalse(
		TEXT("disabled applies do not set helmet vignette"),
		Settings.bOverride_VignetteIntensity);
	TestFalse(
		TEXT("disabled applies do not set color-gain override"),
		Settings.bOverride_ColorGain);
	TestFalse(
		TEXT("disabled applies do not set bloom override"),
		Settings.bOverride_BloomIntensity);
	TestFalse(
		TEXT("disabled applies do not set film-grain override"),
		Settings.bOverride_FilmGrainIntensity);
	TestFalse(
		TEXT("disabled applies do not set auto-exposure override"),
		Settings.bOverride_AutoExposureBias);

	Look->bEnabled = true;
	TestTrue(TEXT("IsEnabled follows bEnabled true"), Look->IsEnabled());
	Look->ApplyHelmetSight(Camera);
	TestEqual(
		TEXT("enabled helmet apply sets blend weight"),
		Camera->PostProcessBlendWeight,
		1.f);
	TestTrue(
		TEXT("enabled helmet apply is the branch under test"),
		Settings.bOverride_SceneFringeIntensity);

	return true;
}

#endif
