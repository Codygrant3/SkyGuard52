#include "SkyguardPauseSettingsWidget.h"

#include "SkyguardGameUserSettings.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Button.h"
#include "Components/CheckBox.h"
#include "Components/Slider.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "GameFramework/PlayerController.h"

namespace
{
	void AddPauseRow(UVerticalBox* Root, UWidget* Widget)
	{
		if (UVerticalBoxSlot* Slot = Root->AddChildToVerticalBox(Widget))
		{
			Slot->SetPadding(FMargin(24.f, 8.f));
		}
	}

	UTextBlock* MakePauseLabel(
		UWidgetTree* WidgetTree,
		const FName Name,
		const FText& Text)
	{
		UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>(
			UTextBlock::StaticClass(),
			Name);
		Label->SetText(Text);
		return Label;
	}
}

void USkyguardPauseSettingsWidget::NativeConstruct()
{
	Super::NativeConstruct();
	if (!WidgetTree || WidgetTree->RootWidget)
	{
		return;
	}

	UVerticalBox* Root = WidgetTree->ConstructWidget<UVerticalBox>(
		UVerticalBox::StaticClass(),
		TEXT("RuntimePauseSettingsRoot"));
	AddPauseRow(Root, MakePauseLabel(
		WidgetTree,
		TEXT("RuntimePauseTitle"),
		NSLOCTEXT("SkyguardPause", "PauseTitle", "Paused")));

	AddPauseRow(Root, MakePauseLabel(
		WidgetTree,
		TEXT("RuntimeMasterVolumeLabel"),
		NSLOCTEXT("SkyguardPause", "MasterVolume", "Master Volume")));
	MasterVolumeSlider = WidgetTree->ConstructWidget<USlider>(
		USlider::StaticClass(),
		TEXT("RuntimeMasterVolumeSlider"));
	MasterVolumeSlider->SetMinValue(0.f);
	MasterVolumeSlider->SetMaxValue(1.f);
	AddPauseRow(Root, MasterVolumeSlider);

	AddPauseRow(Root, MakePauseLabel(
		WidgetTree,
		TEXT("RuntimeMouseSensitivityLabel"),
		NSLOCTEXT("SkyguardPause", "MouseSensitivity", "Mouse Sensitivity")));
	MouseSensitivitySlider = WidgetTree->ConstructWidget<USlider>(
		USlider::StaticClass(),
		TEXT("RuntimeMouseSensitivitySlider"));
	MouseSensitivitySlider->SetMinValue(0.005f);
	MouseSensitivitySlider->SetMaxValue(0.5f);
	AddPauseRow(Root, MouseSensitivitySlider);

	AddPauseRow(Root, MakePauseLabel(
		WidgetTree,
		TEXT("RuntimeInvertLookLabel"),
		NSLOCTEXT("SkyguardPause", "InvertLook", "Invert Vertical Look")));
	InvertLookCheckBox = WidgetTree->ConstructWidget<UCheckBox>(
		UCheckBox::StaticClass(),
		TEXT("RuntimeInvertLookCheckBox"));
	AddPauseRow(Root, InvertLookCheckBox);

	AddPauseRow(Root, MakePauseLabel(
		WidgetTree,
		TEXT("RuntimeCameraShakeLabel"),
		NSLOCTEXT("SkyguardPause", "CameraShake", "Camera Shake")));
	CameraShakeSlider = WidgetTree->ConstructWidget<USlider>(
		USlider::StaticClass(),
		TEXT("RuntimeCameraShakeSlider"));
	CameraShakeSlider->SetMinValue(0.f);
	CameraShakeSlider->SetMaxValue(1.f);
	AddPauseRow(Root, CameraShakeSlider);

	ApplyButton = WidgetTree->ConstructWidget<UButton>(
		UButton::StaticClass(),
		TEXT("RuntimeApplySettingsButton"));
	ApplyButton->AddChild(MakePauseLabel(
		WidgetTree,
		TEXT("RuntimeApplySettingsText"),
		NSLOCTEXT("SkyguardPause", "ApplySettings", "Apply Settings")));
	AddPauseRow(Root, ApplyButton);

	ResumeButton = WidgetTree->ConstructWidget<UButton>(
		UButton::StaticClass(),
		TEXT("RuntimeResumeButton"));
	ResumeButton->AddChild(MakePauseLabel(
		WidgetTree,
		TEXT("RuntimeResumeText"),
		NSLOCTEXT("SkyguardPause", "Resume", "Resume")));
	AddPauseRow(Root, ResumeButton);
	WidgetTree->RootWidget = Root;

	if (USkyguardGameUserSettings* Settings =
		USkyguardGameUserSettings::GetSkyguardGameUserSettings())
	{
		MasterVolumeSlider->SetValue(Settings->GetMasterVolume());
		MouseSensitivitySlider->SetValue(Settings->GetMouseSensitivity());
		InvertLookCheckBox->SetIsChecked(Settings->GetInvertVerticalLook());
		CameraShakeSlider->SetValue(Settings->GetCameraShakeScale());
	}

	MasterVolumeSlider->OnValueChanged.AddUniqueDynamic(
		this,
		&USkyguardPauseSettingsWidget::HandleMasterVolumeChanged);
	MouseSensitivitySlider->OnValueChanged.AddUniqueDynamic(
		this,
		&USkyguardPauseSettingsWidget::HandleMouseSensitivityChanged);
	InvertLookCheckBox->OnCheckStateChanged.AddUniqueDynamic(
		this,
		&USkyguardPauseSettingsWidget::HandleInvertLookChanged);
	CameraShakeSlider->OnValueChanged.AddUniqueDynamic(
		this,
		&USkyguardPauseSettingsWidget::HandleCameraShakeChanged);
	ApplyButton->OnClicked.AddUniqueDynamic(
		this,
		&USkyguardPauseSettingsWidget::HandleApplyClicked);
	ResumeButton->OnClicked.AddUniqueDynamic(
		this,
		&USkyguardPauseSettingsWidget::HandleResumeClicked);
}

void USkyguardPauseSettingsWidget::HandleMasterVolumeChanged(const float Value)
{
	if (USkyguardGameUserSettings* Settings =
		USkyguardGameUserSettings::GetSkyguardGameUserSettings())
	{
		Settings->SetMasterVolume(Value);
	}
}

void USkyguardPauseSettingsWidget::HandleMouseSensitivityChanged(const float Value)
{
	if (USkyguardGameUserSettings* Settings =
		USkyguardGameUserSettings::GetSkyguardGameUserSettings())
	{
		Settings->SetMouseSensitivity(Value);
	}
}

void USkyguardPauseSettingsWidget::HandleInvertLookChanged(const bool bChecked)
{
	if (USkyguardGameUserSettings* Settings =
		USkyguardGameUserSettings::GetSkyguardGameUserSettings())
	{
		Settings->SetInvertVerticalLook(bChecked);
	}
}

void USkyguardPauseSettingsWidget::HandleCameraShakeChanged(const float Value)
{
	if (USkyguardGameUserSettings* Settings =
		USkyguardGameUserSettings::GetSkyguardGameUserSettings())
	{
		Settings->SetCameraShakeScale(Value);
	}
}

void USkyguardPauseSettingsWidget::HandleApplyClicked()
{
	if (USkyguardGameUserSettings* Settings =
		USkyguardGameUserSettings::GetSkyguardGameUserSettings())
	{
		Settings->ApplyAndSaveSettings(false);
	}
}

void USkyguardPauseSettingsWidget::HandleResumeClicked()
{
	HandleApplyClicked();
	if (APlayerController* PC = GetOwningPlayer())
	{
		PC->SetPause(false);
		PC->bShowMouseCursor = false;
		PC->SetInputMode(FInputModeGameOnly());
	}
	RemoveFromParent();
}
