#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMissionDirectorCampaignHelpers.h"

#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardMissionDefinition.h"
#include "Engine/GameInstance.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMissionDirectorCampaignHelpersTests
{
	const FString& AutomationSlot()
	{
		static const FString SlotName = TEXT("SkyguardHelpersNoSlot");
		return SlotName;
	}

	USkyguardCampaignSubsystem* MakeBareCampaign()
	{
		UGameInstance* GameInstance =
			NewObject<UGameInstance>(GetTransientPackage());
		return NewObject<USkyguardCampaignSubsystem>(GameInstance);
	}

	USkyguardCampaignDefinition* MakeMinimalCampaign()
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>(GetTransientPackage());
		Mission->MissionId = TEXT("HelpersM01");
		Mission->DisplayName = FText::FromString(TEXT("Helpers Mission"));
		Mission->CampaignOrder = 1;
		Mission->Route.RouteId = TEXT("HelpersRoute");

		FSkyguardRoutePoint Start;
		Start.PointId = TEXT("Start");
		Start.WorldLocation = FVector::ZeroVector;
		FSkyguardRoutePoint End;
		End.PointId = TEXT("End");
		End.WorldLocation = FVector(1000.f, 0.f, 0.f);
		Mission->Route.Points = { Start, End };

		FSkyguardObjectiveDefinition Required;
		Required.ObjectiveId = TEXT("DestroyTargets");
		Required.DisplayName = FText::FromString(TEXT("Destroy targets"));
		Required.Type = ESkyguardMissionObjectiveType::DestroyTargets;
		Required.RequiredProgress = 1;
		Required.bRequiredForMissionSuccess = true;
		Mission->Objectives = { Required };

		USkyguardCampaignDefinition* Campaign =
			NewObject<USkyguardCampaignDefinition>(GetTransientPackage());
		Campaign->CampaignId = TEXT("HelpersCampaign");
		Campaign->DisplayName = FText::FromString(TEXT("Helpers Campaign"));
		Campaign->Missions = { Mission };
		return Campaign;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionDirectorCampaignHelpersNullCampaignTest,
	"Skyguard52.Campaign.DirectorHelpers.NullCampaignReturnsFalseWithoutCrash",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionDirectorCampaignHelpersNullCampaignTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMissionDirectorCampaignHelpers;
	using namespace SkyguardMissionDirectorCampaignHelpersTests;

	const FString& SlotName = AutomationSlot();
	LoadCampaignProgressAfterConfigure(nullptr, SlotName, 0);
	TestFalse(
		TEXT("FillAndFinalize returns false when Campaign is null"),
		FillAndFinalize(nullptr, nullptr, nullptr, nullptr, SlotName, 0));
	TestFalse(
		TEXT("FillAndFail returns false when Campaign is null"),
		FillAndFail(nullptr, nullptr, nullptr, nullptr, SlotName, 0));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionDirectorCampaignHelpersNamedApiTest,
	"Skyguard52.Campaign.DirectorHelpers.FillAndFailVsFillAndFinalizeHitNamedApis",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionDirectorCampaignHelpersNamedApiTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMissionDirectorCampaignHelpers;
	using namespace SkyguardMissionDirectorCampaignHelpersTests;

	const FString& SlotName = AutomationSlot();
	USkyguardCampaignSubsystem* Bare = MakeBareCampaign();
	if (!TestNotNull(
		TEXT("Campaign subsystem NewObject succeeds without a save slot"),
		Bare))
	{
		return false;
	}

	LoadCampaignProgressAfterConfigure(Bare, SlotName, 0);

	FSkyguardMissionResult FinalizeProbe;
	TestFalse(
		TEXT("FinalizeActiveMission is false with no active mission"),
		Bare->FinalizeActiveMission(FinalizeProbe, SlotName, 0));
	TestFalse(
		TEXT("FillAndFinalize matches FinalizeActiveMission without an active mission"),
		FillAndFinalize(Bare, nullptr, nullptr, nullptr, SlotName, 0));

	FSkyguardMissionResult FailProbe;
	TestFalse(
		TEXT("FailActiveMission is false with no active mission"),
		Bare->FailActiveMission(FailProbe, SlotName, 0));
	TestFalse(
		TEXT("FillAndFail matches FailActiveMission without an active mission"),
		FillAndFail(Bare, nullptr, nullptr, nullptr, SlotName, 0));

	USkyguardCampaignDefinition* Definition = MakeMinimalCampaign();
	USkyguardCampaignSubsystem* FinalizeRuntime = MakeBareCampaign();
	USkyguardCampaignSubsystem* FailRuntime = MakeBareCampaign();
	if (!TestNotNull(TEXT("Minimal campaign definition is created"), Definition) ||
		!TestNotNull(TEXT("Finalize runtime NewObject succeeds"), FinalizeRuntime) ||
		!TestNotNull(TEXT("Fail runtime NewObject succeeds"), FailRuntime))
	{
		return false;
	}

	TestTrue(
		TEXT("Finalize runtime configures in memory"),
		FinalizeRuntime->ConfigureCampaign(Definition));
	TestTrue(
		TEXT("Fail runtime configures in memory"),
		FailRuntime->ConfigureCampaign(Definition));
	LoadCampaignProgressAfterConfigure(FinalizeRuntime, SlotName, 0);
	LoadCampaignProgressAfterConfigure(FailRuntime, SlotName, 0);
	TestTrue(
		TEXT("Finalize runtime starts HelpersM01"),
		FinalizeRuntime->StartMission(TEXT("HelpersM01")));
	TestTrue(
		TEXT("Fail runtime starts HelpersM01"),
		FailRuntime->StartMission(TEXT("HelpersM01")));

	TestFalse(
		TEXT("FillAndFinalize hits FinalizeActiveMission and rejects incomplete objectives"),
		FillAndFinalize(FinalizeRuntime, nullptr, nullptr, nullptr, SlotName, 0));
	TestNotNull(
		TEXT("FillAndFinalize leaves the active mission because FinalizeActiveMission rejected"),
		FinalizeRuntime->GetActiveMission());
	TestEqual(
		TEXT("FillAndFinalize does not publish a debrief when FinalizeActiveMission returns false"),
		FinalizeRuntime->GetLastDebrief().State,
		ESkyguardMissionDebriefState::Unavailable);

	TestTrue(
		TEXT("FillAndFail hits FailActiveMission with an active mission"),
		FillAndFail(FailRuntime, nullptr, nullptr, nullptr, SlotName, 0));
	TestTrue(
		TEXT("FillAndFail clears the active mission through FailActiveMission"),
		FailRuntime->GetActiveMission() == nullptr);
	TestEqual(
		TEXT("FillAndFail publishes the FailActiveMission debrief"),
		FailRuntime->GetLastDebrief().State,
		ESkyguardMissionDebriefState::Ready);
	TestFalse(
		TEXT("FillAndFail does not claim mission success"),
		FailRuntime->GetLastDebrief().Result.bMissionSucceeded);
	TestFalse(
		TEXT("FillAndFail does not persist a save slot"),
		FailRuntime->GetLastDebrief().bProgressSaved);
	return true;
}

#endif
