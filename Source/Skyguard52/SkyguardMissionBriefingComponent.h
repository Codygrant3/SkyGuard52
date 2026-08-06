#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkyguardMissionBriefingComponent.generated.h"

class USkyguardMissionDefinition;

UENUM(BlueprintType)
enum class ESkyguardMissionBriefingState : uint8
{
	Unconfigured,
	Warming,
	Ready,
	Launched
};

/**
 * Deterministic mission-briefing gate.
 *
 * UI code can render the exposed text while mission assets warm. The component
 * deliberately owns no widget or async-load policy; it only prevents a sortie
 * from launching before both the authored minimum reading time and the
 * mission director's readiness signal have been satisfied.
 */
UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardMissionBriefingComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	USkyguardMissionBriefingComponent();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Briefing")
	bool ConfigureFromMission(USkyguardMissionDefinition* Mission);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Briefing")
	void SetAssetsReady(bool bReady);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Briefing")
	void AdvanceBriefing(float DeltaSeconds);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Briefing")
	bool AcknowledgeAndLaunch();

	UFUNCTION(BlueprintPure, Category="Skyguard|Briefing")
	bool CanLaunch() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Briefing")
	ESkyguardMissionBriefingState GetBriefingState() const { return State; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Briefing")
	float GetElapsedSeconds() const { return ElapsedSeconds; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Briefing")
	float GetMinimumWarmupSeconds() const { return MinimumWarmupSeconds; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Briefing")
	FText GetBriefingText() const { return BriefingText; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Briefing")
	TArray<FText> GetRadioChatter() const { return RadioChatter; }

private:
	UPROPERTY(Transient)
	TObjectPtr<USkyguardMissionDefinition> MissionDefinition;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Briefing")
	ESkyguardMissionBriefingState State =
		ESkyguardMissionBriefingState::Unconfigured;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Briefing")
	FText BriefingText;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Briefing")
	TArray<FText> RadioChatter;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Briefing")
	float MinimumWarmupSeconds = 0.f;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Briefing")
	float ElapsedSeconds = 0.f;

	bool bAssetsReady = false;

	void RefreshState();
};
