#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardSortiePresentationComponent.h"

#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardMissionDefinition.h"
#include "Engine/GameInstance.h"
#include "Misc/AutomationTest.h"

namespace SkyguardSortiePresentationTests
{
	static const TCHAR* CampaignPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Campaign_Skyguard52.DA_Campaign_Skyguard52");

	USkyguardCampaignDefinition* LoadCampaign()
	{
		return LoadObject<USkyguardCampaignDefinition>(
			nullptr,
			CampaignPath);
	}

	bool HasCard(
		const TArray<FSkyguardBriefingCard>& Cards,
		const FName CardId)
	{
		return Cards.ContainsByPredicate(
			[CardId](const FSkyguardBriefingCard& Card)
			{
				return Card.CardId == CardId;
			});
	}

	bool HasPictogram(
		const TArray<FSkyguardBriefingCard>& Cards,
		const ESkyguardBriefingPictogram Pictogram)
	{
		return Cards.ContainsByPredicate(
			[Pictogram](const FSkyguardBriefingCard& Card)
			{
				return Card.Pictogram == Pictogram;
			});
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSortieDenseBriefingTest,
	"Skyguard52.Presentation.Sortie.DenseMissionSpecificBriefing",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortieDenseBriefingTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardSortiePresentationTests;
	USkyguardCampaignDefinition* Campaign = LoadCampaign();
	TestNotNull(TEXT("Campaign V1 loads"), Campaign);
	if (!Campaign)
	{
		return false;
	}
	USkyguardMissionDefinition* Mission =
		Campaign->FindMission(TEXT("M01_CoastalIntercept"));
	TestNotNull(TEXT("Mission 1 loads"), Mission);
	if (!Mission)
	{
		return false;
	}

	USkyguardSortiePresentationComponent* Presentation =
		NewObject<USkyguardSortiePresentationComponent>(
			GetTransientPackage());
	TestTrue(TEXT("Presentation derives from governed Mission 1"),
		Presentation->ConfigureFromMission(Mission));
	TestEqual(TEXT("Presentation enters briefing state"),
		Presentation->GetPresentationState(),
		ESkyguardSortiePresentationState::Briefing);
	TestEqual(TEXT("Mission identity binds"),
		Presentation->MissionId, Mission->MissionId);
	TestTrue(TEXT("Mission title binds"),
		Presentation->MissionTitle.EqualTo(Mission->DisplayName));
	TestTrue(TEXT("Authored briefing copy binds"),
		Presentation->BriefingText.EqualTo(
			Mission->Presentation.Briefing));

	const TArray<FSkyguardBriefingCard> Cards =
		Presentation->GetBriefingCards();
	TestTrue(TEXT("Dense briefing provides at least seven cards"),
		Cards.Num() >= 7);
	for (const FName CardId : {
		FName(TEXT("MissionDirective")),
		FName(TEXT("FlightRoute")),
		FName(TEXT("ThreatPicture")),
		FName(TEXT("BossProfile")),
		FName(TEXT("Weather"))})
	{
		TestTrue(
			*FString::Printf(TEXT("Required card %s exists"),
				*CardId.ToString()),
			HasCard(Cards, CardId));
	}
	TestTrue(TEXT("Threat pictogram is present"),
		HasPictogram(
			Cards,
			ESkyguardBriefingPictogram::DroneSwarm));
	TestTrue(TEXT("Protected-asset pictogram is present"),
		HasPictogram(
			Cards,
			ESkyguardBriefingPictogram::ProtectedAsset));
	TestTrue(TEXT("Boss pictogram is present"),
		HasPictogram(Cards, ESkyguardBriefingPictogram::Boss));
	TestEqual(TEXT("All authored radio lines bind"),
		Presentation->GetRadioRows().Num(),
		Mission->Presentation.RadioChatter.Num());

	const TArray<FSkyguardHowToFlyRow> HowTo =
		Presentation->GetHowToFlyRows();
	TestTrue(TEXT("Mission 1 has dense how-to-fly guidance"),
		HowTo.Num() >= 5);
	TestTrue(TEXT("Igla guidance is derived from boss weapon contract"),
		HowTo.ContainsByPredicate(
			[](const FSkyguardHowToFlyRow& Row)
			{
				return Row.StepId == TEXT("EmployIgla") &&
					Row.Pictogram == ESkyguardBriefingPictogram::Igla;
			}));
	TestTrue(TEXT("Protected-objective guidance is derived from objectives"),
		HowTo.ContainsByPredicate(
			[](const FSkyguardHowToFlyRow& Row)
			{
				return Row.StepId == TEXT("ProtectObjective");
			}));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSortieDebriefStateTest,
	"Skyguard52.Presentation.Sortie.DebriefSaveRetryAckAndTravelStates",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortieDebriefStateTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardSortiePresentationTests;
	USkyguardCampaignDefinition* Campaign = LoadCampaign();
	if (!Campaign)
	{
		AddError(TEXT("Campaign V1 did not load."));
		return false;
	}
	USkyguardMissionDefinition* Mission =
		Campaign->FindMission(TEXT("M01_CoastalIntercept"));
	if (!Mission)
	{
		AddError(TEXT("Mission 1 did not load."));
		return false;
	}

	UGameInstance* GameInstance =
		NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Runtime =
		NewObject<USkyguardCampaignSubsystem>(GameInstance);
	TestTrue(TEXT("Campaign configures"),
		Runtime->ConfigureCampaign(Campaign));
	TestTrue(TEXT("Mission 1 starts"),
		Runtime->StartMission(Mission->MissionId));
	for (const FSkyguardObjectiveDefinition& Objective :
		Mission->Objectives)
	{
		if (Objective.bRequiredForMissionSuccess)
		{
			TestTrue(
				*FString::Printf(TEXT("Required objective %s completes"),
					*Objective.ObjectiveId.ToString()),
				Runtime->AddObjectiveProgress(
					Objective.ObjectiveId,
					Objective.RequiredProgress));
		}
	}

	USkyguardSortiePresentationComponent* Presentation =
		NewObject<USkyguardSortiePresentationComponent>(
			GetTransientPackage());
	TestTrue(TEXT("Mission briefing configures"),
		Presentation->ConfigureFromMission(Mission));
	Presentation->BindCampaignRuntime(Runtime);
	Presentation->SetSortieLaunched();
	TestEqual(TEXT("Presentation enters sortie state"),
		Presentation->GetPresentationState(),
		ESkyguardSortiePresentationState::SortieActive);

	FSkyguardMissionResult Result;
	Result.ShotsFired = 12;
	Result.Hits = 12;
	Result.CompletionTimeSeconds = 300.f;
	TestTrue(TEXT("Mission completes even when persistence is rejected"),
		Runtime->FinalizeActiveMission(Result, TEXT("../invalid"), 0));
	Presentation->RefreshDebrief();
	TestEqual(TEXT("Save failure becomes an explicit UI state"),
		Presentation->GetPresentationState(),
		ESkyguardSortiePresentationState::SaveFailure);
	TestFalse(TEXT("Failed persistence is visible in debrief"),
		Presentation->GetDebrief().bProgressSaved);
	TestTrue(TEXT("Authored success debrief reaches presentation"),
		!Presentation->GetDebrief().Narrative.IsEmpty());
	TestTrue(TEXT("Scored result reaches presentation"),
		Presentation->GetDebrief().Result.FinalScore > 0);
	TestTrue(TEXT("Medal reaches presentation"),
		Presentation->GetDebrief().Result.MedalTier > 0);

	const FString SlotName = FString::Printf(
		TEXT("SkyguardPresentation_%s"),
		*FGuid::NewGuid().ToString(EGuidFormats::Digits));
	Runtime->DeleteCampaignSlot(SlotName, 0);
	TestTrue(TEXT("Player can retry persistence"),
		Presentation->RetryProgressSave(SlotName, 0));
	TestEqual(TEXT("Successful retry returns to ready debrief"),
		Presentation->GetPresentationState(),
		ESkyguardSortiePresentationState::DebriefReady);
	TestTrue(TEXT("Successful retry is visible"),
		Presentation->GetDebrief().bProgressSaved);
	TestTrue(TEXT("Player acknowledges debrief"),
		Presentation->AcknowledgeDebrief());
	TestEqual(TEXT("Acknowledged saved sortie becomes travel-ready"),
		Presentation->GetPresentationState(),
		ESkyguardSortiePresentationState::TravelReady);
	TestTrue(TEXT("Campaign travel guard is green"),
		Runtime->CanTravelToNextMission());
	TestTrue(TEXT("Presentation slot is cleaned"),
		Runtime->DeleteCampaignSlot(SlotName, 0));
	return true;
}

#endif
