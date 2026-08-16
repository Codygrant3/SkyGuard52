#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "InputCoreTypes.h"
#include "SkyguardCpgDebrief.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardSortiePresentationComponent.generated.h"

class ASkyguardGunner;
class ASkyguardGunshipSortieDirector;
class ASkyguardPatrolShipBoss;
class USkyguardCampaignSubsystem;
class USkyguardMissionDefinition;

UENUM(BlueprintType)
enum class ESkyguardSortiePresentationState : uint8
{
	Unconfigured,
	Briefing,
	SortieActive,
	DebriefReady,
	SaveFailure,
	TravelReady,
	TravelBlocked,
	CampaignComplete
};

UENUM(BlueprintType)
enum class ESkyguardBriefingPictogram : uint8
{
	Mission,
	Route,
	DroneSwarm,
	ProtectedAsset,
	Boss,
	Rifle,
	Igla,
	Weather,
	Radio
};

USTRUCT(BlueprintType)
struct FSkyguardBriefingCard
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FName CardId;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FText Title;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, meta=(MultiLine="true"))
	FText Body;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardBriefingPictogram Pictogram =
		ESkyguardBriefingPictogram::Mission;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 Priority = 0;
};

USTRUCT(BlueprintType)
struct FSkyguardBriefingRadioRow
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FName LineId;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FText Speaker;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, meta=(MultiLine="true"))
	FText Subtitle;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardBriefingPictogram Pictogram =
		ESkyguardBriefingPictogram::Radio;
};

USTRUCT(BlueprintType)
struct FSkyguardHowToFlyRow
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FName StepId;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FText InputHint;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, meta=(MultiLine="true"))
	FText Instruction;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardBriefingPictogram Pictogram =
		ESkyguardBriefingPictogram::Mission;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(
	FSkyguardSortiePresentationStateChanged,
	ESkyguardSortiePresentationState,
	NewState);

/**
 * UMG-compatible presentation model for briefing and debrief widgets.
 *
 * The component derives display data from governed mission/campaign state and
 * owns no widget tree, textures, or layout. Blueprint widgets can bind to its
 * properties and state event without reimplementing gameplay rules.
 */
UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardSortiePresentationComponent :
	public UActorComponent
{
	GENERATED_BODY()

public:
	USkyguardSortiePresentationComponent();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	bool ConfigureFromMission(USkyguardMissionDefinition* Mission);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	void BindCampaignRuntime(USkyguardCampaignSubsystem* Runtime);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	void SetSortieLaunched();

	/**
	 * UI-safe briefing acknowledgement. Returns true while presentation is in
	 * Briefing (widgets may dismiss overlays without launching).
	 */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	bool AcknowledgeBriefing();

	/** UI-safe launch: advances Briefing/Unconfigured → SortieActive when configured. */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	bool LaunchSortie();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	void RefreshDebrief();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	void BindGunshipDirector(ASkyguardGunshipSortieDirector* Director);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	void CaptureCpgDebrief(
		ASkyguardGunshipSortieDirector* Director,
		ASkyguardGunner* Gunner,
		ASkyguardPatrolShipBoss* Ship);

	UFUNCTION(BlueprintPure, Category="Skyguard|Sortie Presentation")
	bool HasCpgDebrief() const { return CpgDebrief.bValid; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Sortie Presentation")
	FText GetCpgDebriefCopy() const;

	const FSkyguardCpgDebriefSnapshot& GetCpgDebrief() const
	{
		return CpgDebrief;
	}

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	bool SelectLoadoutSlot(int32 Slot);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	bool HandleDebriefKey(FKey Key);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	bool ContinueSortie();

	UFUNCTION(BlueprintPure, Category="Skyguard|Sortie Presentation")
	ESkyguardLoadout GetSelectedLoadout() const
	{
		return CpgDebrief.SelectedLoadout;
	}

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	bool RetryProgressSave(
		const FString& SlotName = TEXT("Skyguard52Campaign"),
		int32 UserIndex = 0);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation")
	bool AcknowledgeDebrief();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Sortie Presentation",
		meta=(WorldContext="WorldContextObject"))
	bool RequestNextMissionTravel(UObject* WorldContextObject);

	UFUNCTION(BlueprintPure, Category="Skyguard|Sortie Presentation")
	bool IsConfigured() const { return MissionDefinition != nullptr; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Sortie Presentation")
	ESkyguardSortiePresentationState GetPresentationState() const
	{
		return PresentationState;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Sortie Presentation")
	TArray<FSkyguardBriefingCard> GetBriefingCards() const
	{
		return BriefingCards;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Sortie Presentation")
	TArray<FSkyguardBriefingRadioRow> GetRadioRows() const
	{
		return RadioRows;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Sortie Presentation")
	TArray<FSkyguardHowToFlyRow> GetHowToFlyRows() const
	{
		return HowToFlyRows;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Sortie Presentation")
	const FSkyguardMissionDebrief& GetDebrief() const { return Debrief; }

	UPROPERTY(BlueprintAssignable, Category="Skyguard|Sortie Presentation")
	FSkyguardSortiePresentationStateChanged OnPresentationStateChanged;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly,
		Category="Skyguard|Sortie Presentation")
	FName MissionId;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly,
		Category="Skyguard|Sortie Presentation")
	FText MissionTitle;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly,
		Category="Skyguard|Sortie Presentation")
	FText BriefingText;

private:
	UPROPERTY(Transient)
	TObjectPtr<USkyguardMissionDefinition> MissionDefinition;

	UPROPERTY(Transient)
	TObjectPtr<USkyguardCampaignSubsystem> CampaignRuntime;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Sortie Presentation")
	ESkyguardSortiePresentationState PresentationState =
		ESkyguardSortiePresentationState::Unconfigured;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Sortie Presentation")
	TArray<FSkyguardBriefingCard> BriefingCards;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Sortie Presentation")
	TArray<FSkyguardBriefingRadioRow> RadioRows;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Sortie Presentation")
	TArray<FSkyguardHowToFlyRow> HowToFlyRows;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Sortie Presentation")
	FSkyguardMissionDebrief Debrief;

	UPROPERTY(Transient)
	TObjectPtr<ASkyguardGunshipSortieDirector> GunshipDirector;

	UPROPERTY(Transient)
	TObjectPtr<ASkyguardGunner> BoundGunner;

	FSkyguardCpgDebriefSnapshot CpgDebrief;

	void BuildBriefingCards();
	void BuildRadioRows();
	void BuildHowToFlyRows();
	void SetPresentationState(ESkyguardSortiePresentationState NewState);
	void AddBriefingCard(
		FName CardId,
		const FText& Title,
		const FText& Body,
		ESkyguardBriefingPictogram Pictogram,
		int32 Priority);
};
