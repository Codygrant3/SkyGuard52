#include "SkyguardMissionBriefingComponent.h"

#include "SkyguardMissionDefinition.h"

USkyguardMissionBriefingComponent::USkyguardMissionBriefingComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

bool USkyguardMissionBriefingComponent::ConfigureFromMission(
	USkyguardMissionDefinition* Mission)
{
	MissionDefinition = Mission;
	BriefingText = FText::GetEmpty();
	RadioChatter.Reset();
	MinimumWarmupSeconds = 0.f;
	ElapsedSeconds = 0.f;
	bAssetsReady = false;
	State = ESkyguardMissionBriefingState::Unconfigured;

	if (!Mission || Mission->Presentation.Briefing.IsEmpty())
	{
		return false;
	}

	BriefingText = Mission->Presentation.Briefing;
	RadioChatter = Mission->Presentation.RadioChatter;
	MinimumWarmupSeconds =
		FMath::Max(0.f, Mission->Presentation.MinimumBriefingWarmupSeconds);
	State = ESkyguardMissionBriefingState::Warming;
	RefreshState();
	return true;
}

void USkyguardMissionBriefingComponent::SetAssetsReady(const bool bReady)
{
	bAssetsReady = bReady;
	RefreshState();
}

void USkyguardMissionBriefingComponent::AdvanceBriefing(const float DeltaSeconds)
{
	if (State == ESkyguardMissionBriefingState::Unconfigured ||
		State == ESkyguardMissionBriefingState::Launched)
	{
		return;
	}
	ElapsedSeconds += FMath::Max(0.f, DeltaSeconds);
	RefreshState();
}

bool USkyguardMissionBriefingComponent::CanLaunch() const
{
	return State == ESkyguardMissionBriefingState::Ready ||
		State == ESkyguardMissionBriefingState::Launched;
}

bool USkyguardMissionBriefingComponent::AcknowledgeAndLaunch()
{
	if (!CanLaunch())
	{
		return false;
	}
	State = ESkyguardMissionBriefingState::Launched;
	return true;
}

void USkyguardMissionBriefingComponent::RefreshState()
{
	if (State == ESkyguardMissionBriefingState::Unconfigured ||
		State == ESkyguardMissionBriefingState::Launched)
	{
		return;
	}
	State = bAssetsReady && ElapsedSeconds >= MinimumWarmupSeconds
		? ESkyguardMissionBriefingState::Ready
		: ESkyguardMissionBriefingState::Warming;
}
