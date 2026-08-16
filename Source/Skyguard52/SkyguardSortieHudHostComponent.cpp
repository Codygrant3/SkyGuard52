#include "SkyguardSortieHudHostComponent.h"

#include "SkyguardSortiePresentationWidgets.h"
#include "Blueprint/UserWidget.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "TimerManager.h"

USkyguardSortieHudHostComponent::USkyguardSortieHudHostComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
	BriefingWidgetClass = USkyguardBriefingWidget::StaticClass();
	DebriefWidgetClass = USkyguardDebriefWidget::StaticClass();
}

void USkyguardSortieHudHostComponent::BeginPlay()
{
	Super::BeginPlay();
	if (!Presentation)
	{
		RebindIfNeeded();
	}
	if (!Presentation)
	{
		GetWorld()->GetTimerManager().SetTimer(
			RebindTimerHandle,
			this,
			&USkyguardSortieHudHostComponent::RebindIfNeeded,
			0.25f,
			false);
	}
	RefreshFromPresentationState();
}

void USkyguardSortieHudHostComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(RebindTimerHandle);
	}
	TearDownWidgets();
	if (Presentation)
	{
		Presentation->OnPresentationStateChanged.RemoveDynamic(
			this,
			&USkyguardSortieHudHostComponent::HandlePresentationStateChanged);
	}
	Super::EndPlay(EndPlayReason);
}

void USkyguardSortieHudHostComponent::RebindIfNeeded()
{
	if (!Presentation)
	{
		BindPresentation(FindPresentationInWorld());
	}
}

bool USkyguardSortieHudHostComponent::ShouldShowDebriefForState(
	const ESkyguardSortiePresentationState State)
{
	switch (State)
	{
	case ESkyguardSortiePresentationState::DebriefReady:
	case ESkyguardSortiePresentationState::SaveFailure:
	case ESkyguardSortiePresentationState::TravelReady:
	case ESkyguardSortiePresentationState::TravelBlocked:
	case ESkyguardSortiePresentationState::CampaignComplete:
		return true;
	case ESkyguardSortiePresentationState::Unconfigured:
	case ESkyguardSortiePresentationState::Briefing:
	case ESkyguardSortiePresentationState::SortieActive:
		return false;
	default:
		ensureMsgf(false, TEXT("Unhandled sortie presentation state."));
		return false;
	}
}

void USkyguardSortieHudHostComponent::BindPresentation(
	USkyguardSortiePresentationComponent* InPresentation)
{
	if (Presentation == InPresentation)
	{
		return;
	}
	if (Presentation)
	{
		Presentation->OnPresentationStateChanged.RemoveDynamic(
			this,
			&USkyguardSortieHudHostComponent::HandlePresentationStateChanged);
	}
	Presentation = InPresentation;
	if (Presentation)
	{
		Presentation->OnPresentationStateChanged.AddDynamic(
			this,
			&USkyguardSortieHudHostComponent::HandlePresentationStateChanged);
	}
	RefreshFromPresentationState();
}

void USkyguardSortieHudHostComponent::RefreshFromPresentationState()
{
	if (!Presentation)
	{
		TearDownWidgets();
		return;
	}

	switch (Presentation->GetPresentationState())
	{
	case ESkyguardSortiePresentationState::Briefing:
		ShowBriefingWidget();
		break;
	case ESkyguardSortiePresentationState::DebriefReady:
	case ESkyguardSortiePresentationState::SaveFailure:
	case ESkyguardSortiePresentationState::TravelReady:
	case ESkyguardSortiePresentationState::TravelBlocked:
	case ESkyguardSortiePresentationState::CampaignComplete:
		ShowDebriefWidget();
		break;
	case ESkyguardSortiePresentationState::Unconfigured:
	case ESkyguardSortiePresentationState::SortieActive:
		TearDownWidgets();
		break;
	default:
		ensureMsgf(false, TEXT("Unhandled sortie presentation state."));
		TearDownWidgets();
		break;
	}
}

void USkyguardSortieHudHostComponent::HandlePresentationStateChanged(
	const ESkyguardSortiePresentationState NewState)
{
	(void)NewState;
	RefreshFromPresentationState();
}

USkyguardSortiePresentationComponent*
USkyguardSortieHudHostComponent::FindPresentationInWorld() const
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return nullptr;
	}
	for (TActorIterator<AActor> It(World); It; ++It)
	{
		if (USkyguardSortiePresentationComponent* Found =
			It->FindComponentByClass<USkyguardSortiePresentationComponent>())
		{
			return Found;
		}
	}
	return nullptr;
}

APlayerController* USkyguardSortieHudHostComponent::ResolvePlayerController() const
{
	if (APlayerController* OwnerPC = Cast<APlayerController>(GetOwner()))
	{
		return OwnerPC;
	}
	if (const APawn* OwnerPawn = Cast<APawn>(GetOwner()))
	{
		return Cast<APlayerController>(OwnerPawn->GetController());
	}
	UWorld* World = GetWorld();
	return World ? World->GetFirstPlayerController() : nullptr;
}

void USkyguardSortieHudHostComponent::ShowBriefingWidget()
{
	APlayerController* PC = ResolvePlayerController();
	if (!PC || !Presentation)
	{
		return;
	}
	if (ActiveDebriefWidget)
	{
		ActiveDebriefWidget->RemoveFromParent();
		ActiveDebriefWidget = nullptr;
	}
	if (ActiveBriefingWidget)
	{
		ActiveBriefingWidget->Configure(Presentation);
		return;
	}
	UClass* WidgetClass = BriefingWidgetClass.LoadSynchronous();
	if (!WidgetClass)
	{
		WidgetClass = USkyguardBriefingWidget::StaticClass();
	}
	ActiveBriefingWidget = CreateWidget<USkyguardBriefingWidget>(PC, WidgetClass);
	if (!ActiveBriefingWidget)
	{
		return;
	}
	ActiveBriefingWidget->Configure(Presentation);
	ActiveBriefingWidget->AddToViewport(BriefingZOrder);
}

void USkyguardSortieHudHostComponent::ShowDebriefWidget()
{
	APlayerController* PC = ResolvePlayerController();
	if (!PC || !Presentation)
	{
		return;
	}
	if (ActiveBriefingWidget)
	{
		ActiveBriefingWidget->RemoveFromParent();
		ActiveBriefingWidget = nullptr;
	}
	if (ActiveDebriefWidget)
	{
		ActiveDebriefWidget->Configure(Presentation);
		ActiveDebriefWidget->SetKeyboardFocus();
		return;
	}
	UClass* WidgetClass = DebriefWidgetClass.LoadSynchronous();
	if (!WidgetClass)
	{
		WidgetClass = USkyguardDebriefWidget::StaticClass();
	}
	ActiveDebriefWidget = CreateWidget<USkyguardDebriefWidget>(PC, WidgetClass);
	if (!ActiveDebriefWidget)
	{
		return;
	}
	ActiveDebriefWidget->Configure(Presentation);
	ActiveDebriefWidget->AddToViewport(DebriefZOrder);
	ActiveDebriefWidget->SetKeyboardFocus();
}

void USkyguardSortieHudHostComponent::TearDownWidgets()
{
	if (ActiveBriefingWidget)
	{
		ActiveBriefingWidget->RemoveFromParent();
		ActiveBriefingWidget = nullptr;
	}
	if (ActiveDebriefWidget)
	{
		ActiveDebriefWidget->RemoveFromParent();
		ActiveDebriefWidget = nullptr;
	}
}
