#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Input/Reply.h"
#include "InputCoreTypes.h"
#include "SkyguardSortiePresentationComponent.h"
#include "SkyguardSortiePresentationWidgets.generated.h"

class UButton;
class UTextBlock;

/**
 * Blueprintable briefing shell. Empty layout is intentional — Blueprint can restyle.
 * Binds to USkyguardSortiePresentationComponent for copy and launch actions.
 */
UCLASS(Blueprintable, BlueprintType)
class SKYGUARD52_API USkyguardBriefingWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|Briefing")
	void Configure(USkyguardSortiePresentationComponent* InPresentation);

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Briefing")
	USkyguardSortiePresentationComponent* GetPresentation() const
	{
		return Presentation;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Briefing")
	FText GetMissionTitle() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Briefing")
	FText GetBriefingText() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Briefing")
	TArray<FSkyguardBriefingCard> GetBriefingCards() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Briefing")
	TArray<FSkyguardBriefingRadioRow> GetRadioRows() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Briefing")
	TArray<FSkyguardHowToFlyRow> GetHowToFlyRows() const;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|Briefing")
	bool AcknowledgeBriefing();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|Briefing")
	bool LaunchSortie();

protected:
	virtual void NativeConstruct() override;

	UPROPERTY(BlueprintReadOnly, Category="Skyguard|Presentation|Briefing")
	TObjectPtr<USkyguardSortiePresentationComponent> Presentation;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> RuntimeTitleText;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> RuntimeBodyText;

	UPROPERTY(Transient)
	TObjectPtr<UButton> RuntimeLaunchButton;

	UFUNCTION()
	void HandleLaunchClicked();

	void RefreshRuntimeLayout();
};

/**
 * Blueprintable debrief shell. Shows narrative / score / save state from presentation.
 */
UCLASS(Blueprintable, BlueprintType)
class SKYGUARD52_API USkyguardDebriefWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	USkyguardDebriefWidget(const FObjectInitializer& ObjectInitializer);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|Debrief")
	void Configure(USkyguardSortiePresentationComponent* InPresentation);

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Debrief")
	USkyguardSortiePresentationComponent* GetPresentation() const
	{
		return Presentation;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Debrief")
	FSkyguardMissionDebrief GetDebrief() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Debrief")
	FText GetDebriefNarrative() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Debrief")
	int32 GetFinalScore() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Debrief")
	bool IsProgressSaved() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|Debrief")
	ESkyguardSortiePresentationState GetPresentationState() const;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|Debrief")
	bool AcknowledgeDebrief();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|Debrief")
	bool RetrySave();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|Debrief")
	bool TravelNext();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|Debrief")
	bool HandleDebriefKey(FKey Key);

protected:
	virtual void NativeConstruct() override;
	virtual FReply NativeOnKeyDown(
		const FGeometry& InGeometry,
		const FKeyEvent& InKeyEvent) override;

	UPROPERTY(BlueprintReadOnly, Category="Skyguard|Presentation|Debrief")
	TObjectPtr<USkyguardSortiePresentationComponent> Presentation;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> RuntimeTitleText;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> RuntimeBodyText;

	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> RuntimeContinueText;

	UPROPERTY(Transient)
	TObjectPtr<UButton> RuntimeContinueButton;

	UFUNCTION()
	void HandleContinueClicked();

	void RefreshRuntimeLayout();
};
