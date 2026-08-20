#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMissionBriefingComponentTests.cpp.
// Empty-state / fail-closed public API only. NewObject, no Gunner spawn,
// no SetAssetsReady, no Ready/Launched warmup path.

namespace SkyguardMissionBriefingFailClosedTests
{
	USkyguardMissionDefinition* MakeEmptyBriefingMission()
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>(GetTransientPackage());
		Mission->MissionId = TEXT("EmptyBriefingReject");
		Mission->DisplayName = FText::FromString(TEXT("Empty Briefing Reject"));
		Mission->Presentation.Briefing = FText::GetEmpty();
		Mission->Presentation.RadioChatter.Add(
			FText::FromString(TEXT("Pilot: holding the coastal orbit.")));
		Mission->Presentation.MinimumBriefingWarmupSeconds = 8.f;
		return Mission;
	}

	USkyguardMissionDefinition* MakeCpgBriefingMission()
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>(GetTransientPackage());
		Mission->MissionId = TEXT("CoastalApproachBriefing");
		Mission->DisplayName = FText::FromString(TEXT("Coastal Approach"));
		Mission->Presentation.Briefing = FText::FromString(
			TEXT("Hold the coastal approach."));
		Mission->Presentation.RadioChatter.Add(
			FText::FromString(TEXT("Pilot: holding the coastal orbit.")));
		Mission->Presentation.MinimumBriefingWarmupSeconds = 4.f;
		return Mission;
	}

	bool ExpectUnconfiguredEmpty(
		FAutomationTestBase& Test,
		USkyguardMissionBriefingComponent& Briefing)
	{
		const bool bState = Test.TestEqual(
			TEXT("state is Unconfigured"),
			Briefing.GetBriefingState(),
			ESkyguardMissionBriefingState::Unconfigured);
		const bool bCanLaunch = Test.TestFalse(
			TEXT("CanLaunch is false"),
			Briefing.CanLaunch());
		const bool bAck = Test.TestFalse(
			TEXT("AcknowledgeAndLaunch is false"),
			Briefing.AcknowledgeAndLaunch());
		const bool bElapsed = Test.TestEqual(
			TEXT("elapsed is 0"),
			Briefing.GetElapsedSeconds(),
			0.f);
		const bool bWarmup = Test.TestEqual(
			TEXT("warmup is 0"),
			Briefing.GetMinimumWarmupSeconds(),
			0.f);
		const bool bText = Test.TestTrue(
			TEXT("briefing text is empty"),
			Briefing.GetBriefingText().IsEmpty());
		const bool bRadio = Test.TestEqual(
			TEXT("radio chatter is empty"),
			Briefing.GetRadioChatter().Num(),
			0);
		return bState && bCanLaunch && bAck && bElapsed && bWarmup && bText &&
			bRadio;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionBriefingFailClosedTest,
	"Skyguard52.Briefing.FailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionBriefingFailClosedTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardMissionBriefingFailClosedTests;

	USkyguardMissionBriefingComponent* Briefing =
		NewObject<USkyguardMissionBriefingComponent>(GetTransientPackage());
	TestNotNull(TEXT("Briefing component is created"), Briefing);
	if (!Briefing)
	{
		return false;
	}

	if (!ExpectUnconfiguredEmpty(*this, *Briefing))
	{
		return false;
	}

	Briefing->AdvanceBriefing(1.5f);
	TestEqual(
		TEXT("AdvanceBriefing while Unconfigured does not increase elapsed"),
		Briefing->GetElapsedSeconds(),
		0.f);
	TestEqual(
		TEXT("AdvanceBriefing while Unconfigured leaves Unconfigured"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Unconfigured);

	TestFalse(
		TEXT("ConfigureFromMission(nullptr) returns false"),
		Briefing->ConfigureFromMission(nullptr));
	if (!ExpectUnconfiguredEmpty(*this, *Briefing))
	{
		return false;
	}

	USkyguardMissionDefinition* EmptyBriefingMission = MakeEmptyBriefingMission();
	TestNotNull(TEXT("Empty-briefing mission is created"), EmptyBriefingMission);
	if (!EmptyBriefingMission)
	{
		return false;
	}
	TestTrue(
		TEXT("Empty-briefing mission Presentation.Briefing is empty"),
		EmptyBriefingMission->Presentation.Briefing.IsEmpty());
	TestFalse(
		TEXT("ConfigureFromMission of empty Presentation.Briefing returns false"),
		Briefing->ConfigureFromMission(EmptyBriefingMission));
	if (!ExpectUnconfiguredEmpty(*this, *Briefing))
	{
		return false;
	}

	USkyguardMissionDefinition* CpgMission = MakeCpgBriefingMission();
	TestNotNull(TEXT("Apache CPG briefing mission is created"), CpgMission);
	if (!CpgMission)
	{
		return false;
	}

	TestTrue(
		TEXT("ConfigureFromMission accepts Apache CPG briefing copy"),
		Briefing->ConfigureFromMission(CpgMission));
	TestEqual(
		TEXT("Successful configure enters Warming"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Warming);
	TestEqual(
		TEXT("Successful configure copies briefing text"),
		Briefing->GetBriefingText().ToString(),
		FString(TEXT("Hold the coastal approach.")));
	TestEqual(
		TEXT("Successful configure copies radio chatter count"),
		Briefing->GetRadioChatter().Num(),
		1);
	if (Briefing->GetRadioChatter().Num() == 1)
	{
		TestEqual(
			TEXT("Successful configure copies radio chatter line"),
			Briefing->GetRadioChatter()[0].ToString(),
			FString(TEXT("Pilot: holding the coastal orbit.")));
	}
	TestEqual(
		TEXT("Successful configure copies clamped warmup"),
		Briefing->GetMinimumWarmupSeconds(),
		4.f);
	TestEqual(
		TEXT("Successful configure zeros elapsed"),
		Briefing->GetElapsedSeconds(),
		0.f);
	TestFalse(TEXT("Warming briefing cannot launch"), Briefing->CanLaunch());
	TestFalse(
		TEXT("AcknowledgeAndLaunch is rejected while Warming"),
		Briefing->AcknowledgeAndLaunch());

	Briefing->AdvanceBriefing(-1.f);
	TestEqual(
		TEXT("AdvanceBriefing(-1.f) does not decrease elapsed"),
		Briefing->GetElapsedSeconds(),
		0.f);
	TestEqual(
		TEXT("AdvanceBriefing(-1.f) leaves Warming"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Warming);

	TestFalse(
		TEXT("ConfigureFromMission(nullptr) after a success returns false"),
		Briefing->ConfigureFromMission(nullptr));
	return ExpectUnconfiguredEmpty(*this, *Briefing);
}

#endif
