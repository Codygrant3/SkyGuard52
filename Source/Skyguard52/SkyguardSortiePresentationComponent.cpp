#include "SkyguardSortiePresentationComponent.h"

#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardMissionDefinition.h"

namespace
{
	FText ObjectiveTypeLabel(const ESkyguardMissionObjectiveType Type)
	{
		switch (Type)
		{
		case ESkyguardMissionObjectiveType::ProtectAsset:
			return FText::FromString(TEXT("PROTECT"));
		case ESkyguardMissionObjectiveType::ReachRoutePoint:
			return FText::FromString(TEXT("NAVIGATE"));
		case ESkyguardMissionObjectiveType::Survive:
			return FText::FromString(TEXT("SURVIVE"));
		case ESkyguardMissionObjectiveType::ScanTargets:
			return FText::FromString(TEXT("IDENTIFY"));
		case ESkyguardMissionObjectiveType::Rescue:
			return FText::FromString(TEXT("RESCUE"));
		case ESkyguardMissionObjectiveType::BossPhase:
			return FText::FromString(TEXT("BOSS"));
		default:
			return FText::FromString(TEXT("ENGAGE"));
		}
	}

	ESkyguardBriefingPictogram ObjectivePictogram(
		const ESkyguardMissionObjectiveType Type)
	{
		switch (Type)
		{
		case ESkyguardMissionObjectiveType::ProtectAsset:
		case ESkyguardMissionObjectiveType::Rescue:
			return ESkyguardBriefingPictogram::ProtectedAsset;
		case ESkyguardMissionObjectiveType::BossPhase:
			return ESkyguardBriefingPictogram::Boss;
		case ESkyguardMissionObjectiveType::ReachRoutePoint:
			return ESkyguardBriefingPictogram::Route;
		default:
			return ESkyguardBriefingPictogram::DroneSwarm;
		}
	}
}

USkyguardSortiePresentationComponent::USkyguardSortiePresentationComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

bool USkyguardSortiePresentationComponent::ConfigureFromMission(
	USkyguardMissionDefinition* Mission)
{
	MissionDefinition = Mission;
	MissionId = NAME_None;
	MissionTitle = FText::GetEmpty();
	BriefingText = FText::GetEmpty();
	BriefingCards.Reset();
	RadioRows.Reset();
	HowToFlyRows.Reset();
	Debrief = FSkyguardMissionDebrief();
	CpgDebrief = FSkyguardCpgDebriefSnapshot();
	if (!Mission || Mission->MissionId.IsNone() ||
		Mission->DisplayName.IsEmpty() ||
		Mission->Presentation.Briefing.IsEmpty())
	{
		SetPresentationState(ESkyguardSortiePresentationState::Unconfigured);
		return false;
	}

	MissionId = Mission->MissionId;
	MissionTitle = Mission->DisplayName;
	BriefingText = Mission->Presentation.Briefing;
	BuildBriefingCards();
	BuildRadioRows();
	BuildHowToFlyRows();
	SetPresentationState(ESkyguardSortiePresentationState::Briefing);
	return true;
}

void USkyguardSortiePresentationComponent::BindCampaignRuntime(
	USkyguardCampaignSubsystem* Runtime)
{
	CampaignRuntime = Runtime;
	RefreshDebrief();
}

void USkyguardSortiePresentationComponent::SetSortieLaunched()
{
	if (MissionDefinition &&
		(PresentationState == ESkyguardSortiePresentationState::Briefing ||
		 PresentationState == ESkyguardSortiePresentationState::Unconfigured))
	{
		CpgDebrief.bValid = false;
		SetPresentationState(ESkyguardSortiePresentationState::SortieActive);
	}
}

bool USkyguardSortiePresentationComponent::AcknowledgeBriefing()
{
	return MissionDefinition != nullptr &&
		PresentationState == ESkyguardSortiePresentationState::Briefing;
}

bool USkyguardSortiePresentationComponent::LaunchSortie()
{
	if (!MissionDefinition)
	{
		return false;
	}
	if (PresentationState != ESkyguardSortiePresentationState::Briefing &&
		PresentationState != ESkyguardSortiePresentationState::Unconfigured)
	{
		return PresentationState == ESkyguardSortiePresentationState::SortieActive;
	}
	SetSortieLaunched();
	return PresentationState == ESkyguardSortiePresentationState::SortieActive;
}

void USkyguardSortiePresentationComponent::RefreshDebrief()
{
	if (!CampaignRuntime)
	{
		return;
	}
	Debrief = CampaignRuntime->GetLastDebrief();
	if (Debrief.State == ESkyguardMissionDebriefState::Unavailable)
	{
		return;
	}
	if (Debrief.State == ESkyguardMissionDebriefState::Ready)
	{
		// Failed sorties intentionally skip progression save; only treat
		// missing persistence as SaveFailure after a successful mission.
		const bool bExpectProgressSave = Debrief.Result.bMissionSucceeded;
		SetPresentationState(
			!bExpectProgressSave || Debrief.bProgressSaved
				? ESkyguardSortiePresentationState::DebriefReady
				: ESkyguardSortiePresentationState::SaveFailure);
		return;
	}
	if (Debrief.bCampaignComplete)
	{
		SetPresentationState(
			ESkyguardSortiePresentationState::CampaignComplete);
	}
	else if (CampaignRuntime->CanTravelToNextMission())
	{
		SetPresentationState(ESkyguardSortiePresentationState::TravelReady);
	}
	else
	{
		SetPresentationState(ESkyguardSortiePresentationState::TravelBlocked);
	}
}

bool USkyguardSortiePresentationComponent::RetryProgressSave(
	const FString& SlotName,
	const int32 UserIndex)
{
	if (!CampaignRuntime ||
		!CampaignRuntime->RetrySaveLastDebrief(SlotName, UserIndex))
	{
		RefreshDebrief();
		return false;
	}
	RefreshDebrief();
	return true;
}

bool USkyguardSortiePresentationComponent::AcknowledgeDebrief()
{
	if (!CampaignRuntime || !CampaignRuntime->AcknowledgeDebrief())
	{
		return false;
	}
	RefreshDebrief();
	return true;
}

bool USkyguardSortiePresentationComponent::RequestNextMissionTravel(
	UObject* WorldContextObject)
{
	return CampaignRuntime &&
		CampaignRuntime->TravelToNextMission(WorldContextObject);
}

void USkyguardSortiePresentationComponent::BindGunshipDirector(
	ASkyguardGunshipSortieDirector* Director)
{
	GunshipDirector = Director;
}

void USkyguardSortiePresentationComponent::CaptureCpgDebrief(
	ASkyguardGunshipSortieDirector* Director,
	ASkyguardGunner* Gunner,
	ASkyguardPatrolShipBoss* Ship)
{
	if (Director)
	{
		GunshipDirector = Director;
	}
	if (Gunner)
	{
		BoundGunner = Gunner;
	}
	CpgDebrief = SkyguardCaptureCpgDebrief(
		GunshipDirector.Get(),
		Gunner ? Gunner : BoundGunner.Get(),
		Ship);
	SetPresentationState(ESkyguardSortiePresentationState::DebriefReady);
}

FText USkyguardSortiePresentationComponent::GetCpgDebriefCopy() const
{
	if (!CpgDebrief.bValid)
	{
		return FText::GetEmpty();
	}
	return FText::FromString(SkyguardBuildCpgDebriefCopy(CpgDebrief));
}

bool USkyguardSortiePresentationComponent::SelectLoadoutSlot(const int32 Slot)
{
	if (Slot < 1 || Slot > 4)
	{
		return false;
	}
	const ESkyguardLoadout Loadout = SkyguardLoadoutFromSlot(Slot);
	CpgDebrief.SelectedLoadout = Loadout;
	CpgDebrief.bValid = true;
	if (GunshipDirector)
	{
		GunshipDirector->SetPendingLoadout(Loadout);
	}
	if (ASkyguardGunner* Gunner = BoundGunner.Get())
	{
		Gunner->ApplyLoadout(Loadout);
		CpgDebrief.CannonReady = Gunner->GetCannonMagazine();
		CpgDebrief.RocketReady = Gunner->GetRocketAmmo();
		CpgDebrief.GuidedReady = Gunner->GetGuidedAmmo();
	}
	return true;
}

bool USkyguardSortiePresentationComponent::HandleDebriefKey(const FKey Key)
{
	if (Key == EKeys::One)
	{
		return SelectLoadoutSlot(1);
	}
	if (Key == EKeys::Two)
	{
		return SelectLoadoutSlot(2);
	}
	if (Key == EKeys::Three)
	{
		return SelectLoadoutSlot(3);
	}
	if (Key == EKeys::Four)
	{
		return SelectLoadoutSlot(4);
	}
	if (Key == EKeys::N || Key == EKeys::Enter || Key == EKeys::Virtual_Accept)
	{
		return ContinueSortie();
	}
	return false;
}

bool USkyguardSortiePresentationComponent::ContinueSortie()
{
	if (GunshipDirector)
	{
		if (!GunshipDirector->IsAwaitingContinue())
		{
			return false;
		}
		GunshipDirector->ConfirmContinue();
		const bool bAdvanced = !GunshipDirector->IsAwaitingContinue();
		if (bAdvanced)
		{
			CpgDebrief.bValid = false;
			SetPresentationState(ESkyguardSortiePresentationState::TravelReady);
		}
		return bAdvanced;
	}
	return AcknowledgeDebrief();
}

void USkyguardSortiePresentationComponent::BuildBriefingCards()
{
	if (!MissionDefinition)
	{
		return;
	}
	AddBriefingCard(
		TEXT("MissionDirective"),
		FText::FromString(TEXT("MISSION DIRECTIVE")),
		MissionDefinition->Presentation.Briefing,
		ESkyguardBriefingPictogram::Mission,
		100);

	float RouteLengthCentimeters = 0.f;
	float AirspeedTotal = 0.f;
	for (int32 Index = 0;
		Index < MissionDefinition->Route.Points.Num();
		++Index)
	{
		const FSkyguardRoutePoint& Point =
			MissionDefinition->Route.Points[Index];
		AirspeedTotal += Point.TargetAirspeedKph;
		if (Index > 0)
		{
			RouteLengthCentimeters += FVector::Distance(
				MissionDefinition->Route.Points[Index - 1].WorldLocation,
				Point.WorldLocation);
		}
	}
	const float AverageAirspeed =
		MissionDefinition->Route.Points.IsEmpty()
			? 0.f
			: AirspeedTotal / MissionDefinition->Route.Points.Num();
	AddBriefingCard(
		TEXT("FlightRoute"),
		FText::FromString(TEXT("FLIGHT ROUTE")),
		FText::FromString(FString::Printf(
			TEXT("%d navigation points | %.1f km route | %.0f km/h planned"),
			MissionDefinition->Route.Points.Num(),
			RouteLengthCentimeters / 100000.f,
			AverageAirspeed)),
		ESkyguardBriefingPictogram::Route,
		90);

	int32 ThreatCount = 0;
	int32 FormationCount = 0;
	for (const FSkyguardEnemyWaveDefinition& Wave :
		MissionDefinition->Waves)
	{
		FormationCount += Wave.Formations.Num();
		for (const FSkyguardEnemyFormationDefinition& Formation :
			Wave.Formations)
		{
			ThreatCount += Formation.UnitCount;
		}
	}
	AddBriefingCard(
		TEXT("ThreatPicture"),
		FText::FromString(TEXT("THREAT PICTURE")),
		FText::FromString(FString::Printf(
			TEXT("%d attack drones | %d formations | %d timed waves"),
			ThreatCount,
			FormationCount,
			MissionDefinition->Waves.Num())),
		ESkyguardBriefingPictogram::DroneSwarm,
		85);

	for (int32 Index = 0;
		Index < MissionDefinition->Objectives.Num();
		++Index)
	{
		const FSkyguardObjectiveDefinition& Objective =
			MissionDefinition->Objectives[Index];
		AddBriefingCard(
			FName(*FString::Printf(TEXT("Objective_%s"),
				*Objective.ObjectiveId.ToString())),
			ObjectiveTypeLabel(Objective.Type),
			FText::FromString(FString::Printf(
				TEXT("%s | %s | %d required"),
				*Objective.DisplayName.ToString(),
				Objective.bRequiredForMissionSuccess
					? TEXT("PRIMARY")
					: TEXT("SECONDARY"),
				Objective.RequiredProgress)),
			ObjectivePictogram(Objective.Type),
			80 - Index);
	}

	if (!MissionDefinition->Boss.BossId.IsNone())
	{
		TSet<FName> RequiredWeapons;
		for (const FSkyguardBossWeakPointDefinition& WeakPoint :
			MissionDefinition->Boss.WeakPoints)
		{
			RequiredWeapons.Add(WeakPoint.RequiredWeapon);
		}
		TArray<FString> WeaponNames;
		for (const FName Weapon : RequiredWeapons)
		{
			WeaponNames.Add(Weapon.ToString());
		}
		WeaponNames.Sort();
		AddBriefingCard(
			TEXT("BossProfile"),
			FText::FromString(TEXT("PRIORITY AIR THREAT")),
			FText::FromString(FString::Printf(
				TEXT("%s | %d weak points | weapons: %s"),
				*MissionDefinition->Boss.Callsign.ToString(),
				MissionDefinition->Boss.WeakPoints.Num(),
				*FString::Join(WeaponNames, TEXT(" + ")))),
			ESkyguardBriefingPictogram::Boss,
			70);
	}

	AddBriefingCard(
		TEXT("Weather"),
		FText::FromString(TEXT("FLIGHT CONDITIONS")),
		FText::FromString(FString::Printf(
			TEXT("%s | %.0f m/s wind | %.0f%% cloud | %.0f%% precipitation"),
			*MissionDefinition->Weather.ProfileId.ToString(),
			MissionDefinition->Weather.WindSpeedMetersPerSecond,
			MissionDefinition->Weather.CloudCoverage * 100.f,
			MissionDefinition->Weather.Precipitation * 100.f)),
		ESkyguardBriefingPictogram::Weather,
		60);
}

void USkyguardSortiePresentationComponent::BuildRadioRows()
{
	if (!MissionDefinition)
	{
		return;
	}
	for (int32 Index = 0;
		Index < MissionDefinition->Presentation.RadioChatter.Num();
		++Index)
	{
		FSkyguardBriefingRadioRow Row;
		Row.LineId = FName(*FString::Printf(
			TEXT("%s_Radio_%02d"),
			*MissionDefinition->MissionId.ToString(),
			Index + 1));
		Row.Speaker = FText::FromString(
			Index == 0 ? TEXT("GROUND CONTROL") : TEXT("YAK-52 PILOT"));
		Row.Subtitle =
			MissionDefinition->Presentation.RadioChatter[Index];
		RadioRows.Add(Row);
	}
}

void USkyguardSortiePresentationComponent::BuildHowToFlyRows()
{
	if (!MissionDefinition)
	{
		return;
	}
	auto AddRow = [this](
		const FName StepId,
		const TCHAR* Input,
		const TCHAR* Instruction,
		const ESkyguardBriefingPictogram Pictogram)
	{
		FSkyguardHowToFlyRow Row;
		Row.StepId = StepId;
		Row.InputHint = FText::FromString(Input);
		Row.Instruction = FText::FromString(Instruction);
		Row.Pictogram = Pictogram;
		HowToFlyRows.Add(Row);
	};
	AddRow(
		TEXT("ScanRearArc"),
		TEXT("MOUSE"),
		TEXT("Scan the rear and side arcs while the pilot flies the authored route."),
		ESkyguardBriefingPictogram::Route);
	AddRow(
		TEXT("AimIronSights"),
		TEXT("HOLD RMB"),
		TEXT("Aim through the rifle's iron sights; no HUD reticle is provided."),
		ESkyguardBriefingPictogram::Rifle);
	AddRow(
		TEXT("FireRifle"),
		TEXT("LMB"),
		TEXT("Use controlled rifle fire on drones and exposed components. Keep the pilot safety arc clear."),
		ESkyguardBriefingPictogram::Rifle);

	bool bNeedsIgla = false;
	bool bProtectsAssets = false;
	for (const FSkyguardBossWeakPointDefinition& WeakPoint :
		MissionDefinition->Boss.WeakPoints)
	{
		bNeedsIgla |= WeakPoint.RequiredWeapon == TEXT("Igla");
	}
	for (const FSkyguardObjectiveDefinition& Objective :
		MissionDefinition->Objectives)
	{
		bProtectsAssets |=
			Objective.Type == ESkyguardMissionObjectiveType::ProtectAsset ||
			Objective.Type == ESkyguardMissionObjectiveType::Rescue;
	}
	if (bNeedsIgla)
	{
		AddRow(
			TEXT("EmployIgla"),
			TEXT("SWITCH + LOCK + LAUNCH"),
			TEXT("Expose the heavy target, hold a stable side aspect for lock, then launch the Igla."),
			ESkyguardBriefingPictogram::Igla);
	}
	if (bProtectsAssets)
	{
		AddRow(
			TEXT("ProtectObjective"),
			TEXT("PRIORITIZE"),
			TEXT("Break off the boss attack when drones threaten the protected objective."),
			ESkyguardBriefingPictogram::ProtectedAsset);
	}
}

void USkyguardSortiePresentationComponent::SetPresentationState(
	const ESkyguardSortiePresentationState NewState)
{
	if (PresentationState == NewState)
	{
		return;
	}
	PresentationState = NewState;
	OnPresentationStateChanged.Broadcast(NewState);
}

void USkyguardSortiePresentationComponent::AddBriefingCard(
	const FName CardId,
	const FText& Title,
	const FText& Body,
	const ESkyguardBriefingPictogram Pictogram,
	const int32 Priority)
{
	FSkyguardBriefingCard Card;
	Card.CardId = CardId;
	Card.Title = Title;
	Card.Body = Body;
	Card.Pictogram = Pictogram;
	Card.Priority = Priority;
	BriefingCards.Add(Card);
}
