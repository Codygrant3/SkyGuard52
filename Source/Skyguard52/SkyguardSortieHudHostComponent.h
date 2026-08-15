#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkyguardSortiePresentationComponent.h"
#include "TimerManager.h"
#include "SkyguardSortieHudHostComponent.generated.h"

class USkyguardBriefingWidget;
class USkyguardDebriefWidget;

/**
 * Lightweight host that creates briefing/debrief UMG shells from presentation state.
 * Soft class refs default to C++ widget classes; Blueprint subclasses can restyle.
 */
UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardSortieHudHostComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	USkyguardSortieHudHostComponent();

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|HUD")
	void BindPresentation(USkyguardSortiePresentationComponent* InPresentation);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|HUD")
	void RefreshFromPresentationState();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|HUD")
	void RebindIfNeeded();

	static bool ShouldShowDebriefForState(
		ESkyguardSortiePresentationState State);

	UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|HUD")
	USkyguardSortiePresentationComponent* GetBoundPresentation() const
	{
		return Presentation;
	}

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Presentation|HUD")
	TSoftClassPtr<USkyguardBriefingWidget> BriefingWidgetClass;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Presentation|HUD")
	TSoftClassPtr<USkyguardDebriefWidget> DebriefWidgetClass;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Presentation|HUD")
	int32 BriefingZOrder = 50;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Presentation|HUD")
	int32 DebriefZOrder = 60;

private:
	UPROPERTY(Transient)
	TObjectPtr<USkyguardSortiePresentationComponent> Presentation;

	UPROPERTY(Transient)
	TObjectPtr<USkyguardBriefingWidget> ActiveBriefingWidget;

	UPROPERTY(Transient)
	TObjectPtr<USkyguardDebriefWidget> ActiveDebriefWidget;

	FTimerHandle RebindTimerHandle;

	UFUNCTION()
	void HandlePresentationStateChanged(ESkyguardSortiePresentationState NewState);

	USkyguardSortiePresentationComponent* FindPresentationInWorld() const;
	APlayerController* ResolvePlayerController() const;
	void ShowBriefingWidget();
	void ShowDebriefWidget();
	void TearDownWidgets();
};
