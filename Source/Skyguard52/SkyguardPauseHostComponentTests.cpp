#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardPauseHostComponent.h"

#include "Components/InputComponent.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPauseHostInputBindingTest,
	"Skyguard52.Settings.PauseHost.BindsPauseInputOnce",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPauseHostInputBindingTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardPauseHostWorld"));
	TestNotNull(TEXT("Automation world is created"), World);
	if (!World)
	{
		return false;
	}

	APlayerController* PC = World->SpawnActor<APlayerController>();
	USkyguardPauseHostComponent* Host =
		NewObject<USkyguardPauseHostComponent>(PC);
	UInputComponent* Input = NewObject<UInputComponent>(PC);
	TestNotNull(TEXT("Player controller is created"), PC);
	TestNotNull(TEXT("Pause host is created"), Host);
	TestNotNull(TEXT("Input component is created"), Input);
	if (!PC || !Host || !Input)
	{
		World->DestroyWorld(false);
		return false;
	}

	TestTrue(TEXT("Pause input binds"), Host->BindPauseInput(Input));
	TestTrue(TEXT("Repeated binding is accepted without duplication"),
		Host->BindPauseInput(Input));
	int32 PauseBindingCount = 0;
	for (int32 Index = 0; Index < Input->GetNumActionBindings(); ++Index)
	{
		const FInputActionBinding& Binding = Input->GetActionBinding(Index);
		PauseBindingCount +=
			Binding.GetActionName() == TEXT("Pause") ? 1 : 0;
	}
	TestEqual(TEXT("Exactly one Pause action binding exists"),
		PauseBindingCount, 1);
	TestFalse(TEXT("Pause menu starts hidden"), Host->IsPauseMenuVisible());

	World->DestroyWorld(false);
	return true;
}

#endif
