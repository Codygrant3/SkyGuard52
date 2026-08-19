#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardMissionDefinition.h"
#include "Engine/GameInstance.h"
#include "Misc/AutomationTest.h"

// Isolated USkyguardCampaignSubsystem public-API coverage.
// No CPG mesh/art, no Harbor retune, no Yak / Gunner / player-Igla / rifle spawn,
// and no write to the default Skyguard52Campaign save slot.

namespace SkyguardCampaignSubsystemTests
{
	static const TCHAR* AuthoredCampaignPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Campaign_Skyguard52.DA_Campaign_Skyguard52");

	USkyguardCampaignDefinition* TryLoadAuthoredCampaign()
	{
		return LoadObject<USkyguardCampaignDefinition>(
			nullptr,
			AuthoredCampaignPath);
	}

	USkyguardCampaignDefinition* MakeIsolatedValidCampaign()
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>(GetTransientPackage());
		Mission->MissionId = TEXT("M01_IsolatedSubsystem");
		Mission->DisplayName = FText::FromString(TEXT("Isolated Subsystem"));
		Mission->CampaignOrder = 1;
		Mission->Route.RouteId = TEXT("M01_Isolated_Route");

		FSkyguardRoutePoint Start;
		Start.PointId = TEXT("Start");
		Start.WorldLocation = FVector::ZeroVector;
		FSkyguardRoutePoint End;
		End.PointId = TEXT("End");
		End.WorldLocation = FVector(1000.f, 0.f, 0.f);
		Mission->Route.Points = { Start, End };

		FSkyguardObjectiveDefinition Hold;
		Hold.ObjectiveId = TEXT("Hold");
		Hold.DisplayName = FText::FromString(TEXT("Hold"));
		Mission->Objectives = { Hold };

		USkyguardCampaignDefinition* Campaign =
			NewObject<USkyguardCampaignDefinition>(GetTransientPackage());
		Campaign->CampaignId = TEXT("IsolatedCampaignSubsystem");
		Campaign->DisplayName = FText::FromString(TEXT("Isolated Campaign Subsystem"));
		Campaign->Missions = { Mission };
		return Campaign;
	}

	USkyguardMissionDefinition* FindFirstUnlockedMission(
		const USkyguardCampaignSubsystem& Runtime,
		const USkyguardCampaignDefinition& Campaign)
	{
		USkyguardMissionDefinition* FirstUnlocked = nullptr;
		for (USkyguardMissionDefinition* Mission : Campaign.Missions)
		{
			if (!Mission || !Runtime.CanStartMission(Mission->MissionId))
			{
				continue;
			}
			if (!FirstUnlocked ||
				Mission->CampaignOrder < FirstUnlocked->CampaignOrder)
			{
				FirstUnlocked = Mission;
			}
		}
		return FirstUnlocked;
	}

	FString MakeThrowawaySlotName()
	{
		return FString::Printf(
			TEXT("SgCampSubsys_%s"),
			*FGuid::NewGuid().ToString(EGuidFormats::Digits));
	}

	void AssertFailClosedBeforeConfigure(
		FAutomationTestBase& Test,
		USkyguardCampaignSubsystem& Runtime,
		const FString& ThrowawaySlot)
	{
		Test.TestFalse(
			TEXT("ConfigureCampaign(nullptr) returns false"),
			Runtime.ConfigureCampaign(nullptr));

		const FName AnyIds[] = {
			NAME_None,
			TEXT("M01"),
			TEXT("M01_CoastalIntercept"),
			TEXT("DoesNotExist")
		};
		for (const FName MissionId : AnyIds)
		{
			Test.TestFalse(
				*FString::Printf(
					TEXT("CanStartMission(%s) is false before configure"),
					*MissionId.ToString()),
				Runtime.CanStartMission(MissionId));
			Test.TestFalse(
				*FString::Printf(
					TEXT("StartMission(%s) is fail-closed before configure"),
					*MissionId.ToString()),
				Runtime.StartMission(MissionId));
			Test.TestFalse(
				*FString::Printf(
					TEXT("IsMissionUnlocked(%s) is fail-closed before configure"),
					*MissionId.ToString()),
				Runtime.IsMissionUnlocked(MissionId));
		}

		Test.TestNull(
			TEXT("GetActiveMission is nullptr before configure"),
			Runtime.GetActiveMission());
		Test.TestNull(
			TEXT("GetObjectiveRuntime is nullptr before configure"),
			Runtime.GetObjectiveRuntime());
		Test.TestNull(
			TEXT("GetRouteRuntime is nullptr before configure"),
			Runtime.GetRouteRuntime());
		Test.TestEqual(
			TEXT("GetEarnedCampaignMedals is 0 before configure"),
			Runtime.GetEarnedCampaignMedals(),
			0);

		FSkyguardMissionResult Result;
		Test.TestFalse(
			TEXT("FailActiveMission is fail-closed with no active mission"),
			Runtime.FailActiveMission(Result, ThrowawaySlot, 0));
		Test.TestFalse(
			TEXT("FinalizeActiveMission is fail-closed with no active mission"),
			Runtime.FinalizeActiveMission(Result, ThrowawaySlot, 0));
		Test.TestFalse(
			TEXT("CompleteActiveMission is fail-closed with no active mission"),
			Runtime.CompleteActiveMission(Result));
		Test.TestFalse(
			TEXT("AcknowledgeDebrief is fail-closed with no active mission"),
			Runtime.AcknowledgeDebrief());
		Test.TestFalse(
			TEXT("RetrySaveLastDebrief is fail-closed with no active mission"),
			Runtime.RetrySaveLastDebrief(ThrowawaySlot, 0));
		Test.TestFalse(
			TEXT("TravelToNextMission is fail-closed with no active mission"),
			Runtime.TravelToNextMission(nullptr));
		Test.TestFalse(
			TEXT("CanTravelToNextMission is fail-closed with no active mission"),
			Runtime.CanTravelToNextMission());
	}

	void AssertConfigureAndStartFirstUnlocked(
		FAutomationTestBase& Test,
		USkyguardCampaignSubsystem& Runtime,
		USkyguardCampaignDefinition& Campaign)
	{
		Test.TestTrue(
			TEXT("ConfigureCampaign succeeds for a valid definition"),
			Runtime.ConfigureCampaign(&Campaign));
		Test.TestFalse(
			TEXT("Unknown mission stays locked after configure"),
			Runtime.CanStartMission(TEXT("DoesNotExist")));
		Test.TestFalse(
			TEXT("StartMission is fail-closed for an unknown mission"),
			Runtime.StartMission(TEXT("DoesNotExist")));
		Test.TestFalse(
			TEXT("IsMissionUnlocked is fail-closed for an unknown mission"),
			Runtime.IsMissionUnlocked(TEXT("DoesNotExist")));
		Test.TestNull(
			TEXT("GetActiveMission stays nullptr until StartMission succeeds"),
			Runtime.GetActiveMission());
		Test.TestNull(
			TEXT("GetObjectiveRuntime stays nullptr until StartMission succeeds"),
			Runtime.GetObjectiveRuntime());
		Test.TestNull(
			TEXT("GetRouteRuntime stays nullptr until StartMission succeeds"),
			Runtime.GetRouteRuntime());

		USkyguardMissionDefinition* FirstUnlocked =
			FindFirstUnlockedMission(Runtime, Campaign);
		Test.TestNotNull(
			TEXT("A valid campaign exposes at least one unlocked mission"),
			FirstUnlocked);
		if (!FirstUnlocked)
		{
			return;
		}

		Test.TestTrue(
			TEXT("CanStartMission is true for the first unlocked mission"),
			Runtime.CanStartMission(FirstUnlocked->MissionId));
		Test.TestTrue(
			TEXT("StartMission succeeds for the first unlocked mission"),
			Runtime.StartMission(FirstUnlocked->MissionId));
		Test.TestTrue(
			TEXT("GetActiveMission is the first unlocked mission"),
			Runtime.GetActiveMission() == FirstUnlocked);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignSubsystemSlotNameTest,
	"Skyguard52.Campaign.Subsystem.IsValidCampaignSlotName",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignSubsystemSlotNameTest::RunTest(const FString& Parameters)
{
	TestTrue(
		TEXT("Simple legal name Skyguard52Campaign is accepted"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(
			TEXT("Skyguard52Campaign")));

	TestFalse(
		TEXT("Empty slot names fail"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("")));
	TestFalse(
		TEXT("Whitespace-only slot names fail"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("  ")));
	TestFalse(
		TEXT("Path-separator slot names fail"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("slot/name")));
	TestFalse(
		TEXT("Reserved-character slot names fail"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("slot*name")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignSubsystemPublicApiFailClosedTest,
	"Skyguard52.Campaign.Subsystem.PublicApiFailClosedAndConfigure",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignSubsystemPublicApiFailClosedTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardCampaignSubsystemTests;

	const FString ThrowawaySlot = MakeThrowawaySlotName();
	UGameInstance* GameInstance =
		NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Runtime =
		NewObject<USkyguardCampaignSubsystem>(GameInstance);
	TestNotNull(TEXT("Campaign subsystem constructs on a GameInstance"), Runtime);
	if (!Runtime)
	{
		return false;
	}

	Runtime->DeleteCampaignSlot(ThrowawaySlot, 0);
	AssertFailClosedBeforeConfigure(*this, *Runtime, ThrowawaySlot);

	USkyguardCampaignDefinition* Campaign = TryLoadAuthoredCampaign();
	if (Campaign)
	{
		AssertConfigureAndStartFirstUnlocked(*this, *Runtime, *Campaign);
	}
	else
	{
		AddWarning(FString::Printf(
			TEXT("DA_Campaign_Skyguard52 missing at %s; "
				"null/fail-closed checks still ran. Trying an in-memory "
				"USkyguardCampaignDefinition if ValidateDefinition passes."),
			AuthoredCampaignPath));

		USkyguardCampaignDefinition* Isolated = MakeIsolatedValidCampaign();
		TArray<FText> Errors;
		if (Isolated && Isolated->ValidateDefinition(Errors))
		{
			AssertConfigureAndStartFirstUnlocked(*this, *Runtime, *Isolated);
		}
		else
		{
			AddWarning(TEXT(
				"In-memory campaign did not pass ValidateDefinition; "
				"skipped ConfigureCampaign / StartMission coverage."));
		}
	}

	Runtime->DeleteCampaignSlot(ThrowawaySlot, 0);
	return true;
}

#endif
