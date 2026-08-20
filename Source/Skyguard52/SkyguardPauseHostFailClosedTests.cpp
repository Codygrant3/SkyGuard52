#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardPauseHostComponent.h"

#include "SkyguardPauseSettingsWidget.h"
#include "Components/InputComponent.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardPauseHostComponentTests.cpp.
// Remaining fail-closed public API only: NewObject, no world spawn,
// no Gunner / Yak / Igla / rifle, no ApplyWeaponHit. Existing
// SkyguardPauseHostComponentTests.cpp already covers BindPauseInput
// once on the same UInputComponent with a spawned PlayerController.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPauseHostFailClosedTest,
	"Skyguard52.Settings.PauseHost.FailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPauseHostFailClosedTest::RunTest(const FString& Parameters)
{
	USkyguardPauseHostComponent* Host =
		NewObject<USkyguardPauseHostComponent>(GetTransientPackage());
	TestNotNull(TEXT("NewObject pause host constructs"), Host);
	if (!Host)
	{
		return false;
	}

	TestFalse(
		TEXT("NewObject default IsPauseMenuVisible is false"),
		Host->IsPauseMenuVisible());
	TestEqual(
		TEXT("NewObject default PauseWidgetZOrder is 100"),
		Host->PauseWidgetZOrder,
		100);
	TestFalse(
		TEXT("Constructor disables PrimaryComponentTick"),
		Host->PrimaryComponentTick.bCanEverTick);
	TestTrue(
		TEXT("Constructor PauseWidgetClass is USkyguardPauseSettingsWidget"),
		Host->PauseWidgetClass.Get() ==
			USkyguardPauseSettingsWidget::StaticClass());

	TestFalse(
		TEXT("BindPauseInput(nullptr) is fail-closed"),
		Host->BindPauseInput(nullptr));
	TestFalse(
		TEXT("Null bind leaves IsPauseMenuVisible false"),
		Host->IsPauseMenuVisible());

	UInputComponent* FirstInput =
		NewObject<UInputComponent>(GetTransientPackage());
	UInputComponent* SecondInput =
		NewObject<UInputComponent>(GetTransientPackage());
	TestNotNull(TEXT("First NewObject UInputComponent constructs"), FirstInput);
	TestNotNull(TEXT("Second NewObject UInputComponent constructs"), SecondInput);
	if (!FirstInput || !SecondInput)
	{
		return false;
	}

	TestTrue(
		TEXT("BindPauseInput accepts the first UInputComponent"),
		Host->BindPauseInput(FirstInput));
	TestFalse(
		TEXT("BindPauseInput rejects a different UInputComponent after bind"),
		Host->BindPauseInput(SecondInput));
	TestTrue(
		TEXT("BindPauseInput accepts the already-bound UInputComponent"),
		Host->BindPauseInput(FirstInput));
	TestFalse(
		TEXT("Successful bind leaves IsPauseMenuVisible false"),
		Host->IsPauseMenuVisible());

	Host->TogglePause();
	TestFalse(
		TEXT("TogglePause with no PlayerController owner is a no-op"),
		Host->IsPauseMenuVisible());

	return true;
}

#endif
