#include "SkyguardSortiePresentationWidgets.h"

#include "SkyguardMissionBriefingComponent.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Blueprint/WidgetTree.h"

namespace
{
	void AddRuntimeRow(UVerticalBox* Root, UWidget* Widget)
	{
		if (UVerticalBoxSlot* Slot = Root->AddChildToVerticalBox(Widget))
		{
			Slot->SetPadding(FMargin(24.f, 10.f));
		}
	}
}

void USkyguardBriefingWidget::NativeConstruct()
{
	Super::NativeConstruct();
	if (!WidgetTree || WidgetTree->RootWidget)
	{
		RefreshRuntimeLayout();
		return;
	}

	UVerticalBox* Root = WidgetTree->ConstructWidget<UVerticalBox>(
		UVerticalBox::StaticClass(),
		TEXT("RuntimeBriefingRoot"));
	RuntimeTitleText = WidgetTree->ConstructWidget<UTextBlock>(
		UTextBlock::StaticClass(),
		TEXT("RuntimeMissionTitle"));
	RuntimeBodyText = WidgetTree->ConstructWidget<UTextBlock>(
		UTextBlock::StaticClass(),
		TEXT("RuntimeBriefingBody"));
	RuntimeLaunchButton = WidgetTree->ConstructWidget<UButton>(
		UButton::StaticClass(),
		TEXT("RuntimeLaunchButton"));
	UTextBlock* LaunchText = WidgetTree->ConstructWidget<UTextBlock>(
		UTextBlock::StaticClass(),
		TEXT("RuntimeLaunchText"));
	LaunchText->SetText(NSLOCTEXT(
		"SkyguardPresentation",
		"LaunchSortie",
		"Launch Sortie"));
	RuntimeBodyText->SetAutoWrapText(true);
	RuntimeLaunchButton->AddChild(LaunchText);
	RuntimeLaunchButton->OnClicked.AddUniqueDynamic(
		this,
		&USkyguardBriefingWidget::HandleLaunchClicked);
	AddRuntimeRow(Root, RuntimeTitleText);
	AddRuntimeRow(Root, RuntimeBodyText);
	AddRuntimeRow(Root, RuntimeLaunchButton);
	WidgetTree->RootWidget = Root;
	RefreshRuntimeLayout();
}

void USkyguardBriefingWidget::Configure(
	USkyguardSortiePresentationComponent* InPresentation)
{
	Presentation = InPresentation;
	RefreshRuntimeLayout();
}

void USkyguardBriefingWidget::RefreshRuntimeLayout()
{
	if (RuntimeTitleText)
	{
		RuntimeTitleText->SetText(GetMissionTitle());
	}
	if (RuntimeBodyText)
	{
		RuntimeBodyText->SetText(GetBriefingText());
	}
}

void USkyguardBriefingWidget::HandleLaunchClicked()
{
	LaunchSortie();
}

FText USkyguardBriefingWidget::GetMissionTitle() const
{
	return Presentation ? Presentation->MissionTitle : FText::GetEmpty();
}

FText USkyguardBriefingWidget::GetBriefingText() const
{
	return Presentation ? Presentation->BriefingText : FText::GetEmpty();
}

TArray<FSkyguardBriefingCard> USkyguardBriefingWidget::GetBriefingCards() const
{
	return Presentation
		? Presentation->GetBriefingCards()
		: TArray<FSkyguardBriefingCard>();
}

TArray<FSkyguardBriefingRadioRow> USkyguardBriefingWidget::GetRadioRows() const
{
	return Presentation
		? Presentation->GetRadioRows()
		: TArray<FSkyguardBriefingRadioRow>();
}

TArray<FSkyguardHowToFlyRow> USkyguardBriefingWidget::GetHowToFlyRows() const
{
	return Presentation
		? Presentation->GetHowToFlyRows()
		: TArray<FSkyguardHowToFlyRow>();
}

bool USkyguardBriefingWidget::AcknowledgeBriefing()
{
	return Presentation && Presentation->AcknowledgeBriefing();
}

bool USkyguardBriefingWidget::LaunchSortie()
{
	if (!Presentation || !Presentation->LaunchSortie())
	{
		return false;
	}

	UWorld* World = GetWorld();
	if (!World)
	{
		return true;
	}
	for (TActorIterator<AActor> It(World); It; ++It)
	{
		USkyguardMissionBriefingComponent* Briefing =
			It->FindComponentByClass<USkyguardMissionBriefingComponent>();
		if (Briefing && Briefing->CanLaunch())
		{
			Briefing->AcknowledgeAndLaunch();
			break;
		}
	}
	return true;
}

void USkyguardDebriefWidget::NativeConstruct()
{
	Super::NativeConstruct();
	if (!WidgetTree || WidgetTree->RootWidget)
	{
		RefreshRuntimeLayout();
		return;
	}

	UVerticalBox* Root = WidgetTree->ConstructWidget<UVerticalBox>(
		UVerticalBox::StaticClass(),
		TEXT("RuntimeDebriefRoot"));
	RuntimeTitleText = WidgetTree->ConstructWidget<UTextBlock>(
		UTextBlock::StaticClass(),
		TEXT("RuntimeDebriefTitle"));
	RuntimeBodyText = WidgetTree->ConstructWidget<UTextBlock>(
		UTextBlock::StaticClass(),
		TEXT("RuntimeDebriefBody"));
	RuntimeContinueButton = WidgetTree->ConstructWidget<UButton>(
		UButton::StaticClass(),
		TEXT("RuntimeContinueButton"));
	RuntimeContinueText = WidgetTree->ConstructWidget<UTextBlock>(
		UTextBlock::StaticClass(),
		TEXT("RuntimeContinueText"));
	RuntimeBodyText->SetAutoWrapText(true);
	RuntimeContinueButton->AddChild(RuntimeContinueText);
	RuntimeContinueButton->OnClicked.AddUniqueDynamic(
		this,
		&USkyguardDebriefWidget::HandleContinueClicked);
	AddRuntimeRow(Root, RuntimeTitleText);
	AddRuntimeRow(Root, RuntimeBodyText);
	AddRuntimeRow(Root, RuntimeContinueButton);
	WidgetTree->RootWidget = Root;
	RefreshRuntimeLayout();
}

void USkyguardDebriefWidget::Configure(
	USkyguardSortiePresentationComponent* InPresentation)
{
	Presentation = InPresentation;
	RefreshRuntimeLayout();
}

void USkyguardDebriefWidget::RefreshRuntimeLayout()
{
	if (RuntimeTitleText)
	{
		RuntimeTitleText->SetText(NSLOCTEXT(
			"SkyguardPresentation",
			"SortieDebrief",
			"Sortie Debrief"));
	}
	if (RuntimeBodyText)
	{
		RuntimeBodyText->SetText(FText::Format(
			NSLOCTEXT(
				"SkyguardPresentation",
				"DebriefRuntimeBody",
				"{0}\n\nFinal score: {1}\nProgress saved: {2}"),
			GetDebriefNarrative(),
			FText::AsNumber(GetFinalScore()),
			IsProgressSaved()
				? NSLOCTEXT("SkyguardPresentation", "SavedYes", "Yes")
				: NSLOCTEXT("SkyguardPresentation", "SavedNo", "No")));
	}
	if (!RuntimeContinueText || !RuntimeContinueButton)
	{
		return;
	}

	switch (GetPresentationState())
	{
	case ESkyguardSortiePresentationState::SaveFailure:
		RuntimeContinueText->SetText(NSLOCTEXT(
			"SkyguardPresentation", "RetrySave", "Retry Save"));
		RuntimeContinueButton->SetIsEnabled(true);
		break;
	case ESkyguardSortiePresentationState::TravelReady:
		RuntimeContinueText->SetText(NSLOCTEXT(
			"SkyguardPresentation", "NextMission", "Next Mission"));
		RuntimeContinueButton->SetIsEnabled(true);
		break;
	case ESkyguardSortiePresentationState::TravelBlocked:
		RuntimeContinueText->SetText(NSLOCTEXT(
			"SkyguardPresentation", "TravelBlocked", "Travel Blocked"));
		RuntimeContinueButton->SetIsEnabled(false);
		break;
	case ESkyguardSortiePresentationState::CampaignComplete:
		RuntimeContinueText->SetText(NSLOCTEXT(
			"SkyguardPresentation", "CloseCampaign", "Close"));
		RuntimeContinueButton->SetIsEnabled(true);
		break;
	case ESkyguardSortiePresentationState::DebriefReady:
	case ESkyguardSortiePresentationState::Unconfigured:
	case ESkyguardSortiePresentationState::Briefing:
	case ESkyguardSortiePresentationState::SortieActive:
		RuntimeContinueText->SetText(NSLOCTEXT(
			"SkyguardPresentation", "Continue", "Continue"));
		RuntimeContinueButton->SetIsEnabled(
			GetPresentationState() ==
				ESkyguardSortiePresentationState::DebriefReady);
		break;
	default:
		ensureMsgf(false, TEXT("Unhandled sortie presentation state."));
		RuntimeContinueButton->SetIsEnabled(false);
		break;
	}
}

void USkyguardDebriefWidget::HandleContinueClicked()
{
	if (!Presentation)
	{
		return;
	}

	switch (Presentation->GetPresentationState())
	{
	case ESkyguardSortiePresentationState::DebriefReady:
		AcknowledgeDebrief();
		break;
	case ESkyguardSortiePresentationState::SaveFailure:
		RetrySave();
		break;
	case ESkyguardSortiePresentationState::TravelReady:
		TravelNext();
		break;
	case ESkyguardSortiePresentationState::CampaignComplete:
		RemoveFromParent();
		break;
	case ESkyguardSortiePresentationState::TravelBlocked:
	case ESkyguardSortiePresentationState::Unconfigured:
	case ESkyguardSortiePresentationState::Briefing:
	case ESkyguardSortiePresentationState::SortieActive:
		break;
	default:
		ensureMsgf(false, TEXT("Unhandled sortie presentation state."));
		break;
	}
	RefreshRuntimeLayout();
}

FSkyguardMissionDebrief USkyguardDebriefWidget::GetDebrief() const
{
	return Presentation ? Presentation->GetDebrief() : FSkyguardMissionDebrief();
}

FText USkyguardDebriefWidget::GetDebriefNarrative() const
{
	return Presentation ? Presentation->GetDebrief().Narrative : FText::GetEmpty();
}

int32 USkyguardDebriefWidget::GetFinalScore() const
{
	return Presentation ? Presentation->GetDebrief().Result.FinalScore : 0;
}

bool USkyguardDebriefWidget::IsProgressSaved() const
{
	return Presentation && Presentation->GetDebrief().bProgressSaved;
}

ESkyguardSortiePresentationState USkyguardDebriefWidget::GetPresentationState() const
{
	return Presentation
		? Presentation->GetPresentationState()
		: ESkyguardSortiePresentationState::Unconfigured;
}

bool USkyguardDebriefWidget::AcknowledgeDebrief()
{
	return Presentation && Presentation->AcknowledgeDebrief();
}

bool USkyguardDebriefWidget::RetrySave()
{
	return Presentation && Presentation->RetryProgressSave();
}

bool USkyguardDebriefWidget::TravelNext()
{
	return Presentation && Presentation->RequestNextMissionTravel(this);
}
