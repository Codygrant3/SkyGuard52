#include "SkyguardPauseHostComponent.h"

#include "SkyguardPauseSettingsWidget.h"
#include "Blueprint/UserWidget.h"
#include "Components/InputComponent.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"

USkyguardPauseHostComponent::USkyguardPauseHostComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
	PauseWidgetClass = USkyguardPauseSettingsWidget::StaticClass();
}

void USkyguardPauseHostComponent::BeginPlay()
{
	Super::BeginPlay();
	if (APlayerController* PC = ResolvePlayerController())
	{
		BindPauseInput(PC->InputComponent);
	}
}

bool USkyguardPauseHostComponent::BindPauseInput(
	UInputComponent* InputComponent)
{
	if (!InputComponent)
	{
		return false;
	}
	if (BoundInputComponent.IsValid())
	{
		return BoundInputComponent.Get() == InputComponent;
	}

	FInputActionBinding& Binding = InputComponent->BindAction(
		TEXT("Pause"),
		IE_Pressed,
		this,
		&USkyguardPauseHostComponent::TogglePause);
	Binding.bConsumeInput = true;
	Binding.bExecuteWhenPaused = true;
	BoundInputComponent = InputComponent;
	return true;
}

bool USkyguardPauseHostComponent::IsPauseMenuVisible() const
{
	return ActiveWidget && ActiveWidget->IsInViewport();
}

APlayerController* USkyguardPauseHostComponent::ResolvePlayerController() const
{
	return Cast<APlayerController>(GetOwner());
}

void USkyguardPauseHostComponent::ResumeGame(
	APlayerController* PlayerController)
{
	PlayerController->SetPause(false);
	PlayerController->bShowMouseCursor = false;
	PlayerController->SetInputMode(FInputModeGameOnly());
	if (ActiveWidget)
	{
		ActiveWidget->RemoveFromParent();
	}
}

void USkyguardPauseHostComponent::TogglePause()
{
	APlayerController* PC = ResolvePlayerController();
	if (!PC)
	{
		return;
	}
	if (IsPauseMenuVisible() || UGameplayStatics::IsGamePaused(this))
	{
		ResumeGame(PC);
		return;
	}

	if (!ActiveWidget)
	{
		UClass* WidgetClass = PauseWidgetClass.LoadSynchronous();
		if (!WidgetClass)
		{
			WidgetClass = USkyguardPauseSettingsWidget::StaticClass();
		}
		ActiveWidget = CreateWidget<USkyguardPauseSettingsWidget>(
			PC,
			WidgetClass);
	}
	if (!ActiveWidget || (!PC->SetPause(true) &&
		!UGameplayStatics::IsGamePaused(this)))
	{
		return;
	}

	ActiveWidget->AddToViewport(PauseWidgetZOrder);
	PC->bShowMouseCursor = true;
	// GameAndUI keeps Pause (Escape) executable while paused; Resume button also works.
	FInputModeGameAndUI InputMode;
	InputMode.SetWidgetToFocus(ActiveWidget->TakeWidget());
	InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	InputMode.SetHideCursorDuringCapture(false);
	PC->SetInputMode(InputMode);
}
