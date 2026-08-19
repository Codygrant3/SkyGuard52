#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"

#include "Misc/AutomationTest.h"

namespace SkyguardMissionBriefingComponentTests
{
	USkyguardMissionDefinition* MakeBriefingMission(const float WarmupSeconds)
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>(GetTransientPackage());
		Mission->MissionId = TEXT("BriefingLaunchGate");
		Mission->DisplayName = FText::FromString(TEXT("Briefing Launch Gate"));
		Mission->Presentation.Briefing = FText::FromString(
			TEXT("Hold the coastal approach. Prioritize the threat that can kill the ship."));
		Mission->Presentation.MinimumBriefingWarmupSeconds = WarmupSeconds;
		return Mission;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionBriefingLaunchGateTest,
	"Skyguard52.Briefing.LaunchGateRequiresWarmupAndAssetsReady",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionBriefingLaunchGateTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardMissionBriefingComponentTests;

	USkyguardMissionBriefingComponent* Briefing =
		NewObject<USkyguardMissionBriefingComponent>(GetTransientPackage());
	TestNotNull(TEXT("Briefing component is created"), Briefing);
	if (!Briefing)
	{
		return false;
	}

	TestEqual(
		TEXT("Briefing starts Unconfigured"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Unconfigured);
	TestFalse(TEXT("Unconfigured briefing cannot launch"), Briefing->CanLaunch());
	TestFalse(
		TEXT("AcknowledgeAndLaunch is rejected while Unconfigured"),
		Briefing->AcknowledgeAndLaunch());

	USkyguardMissionDefinition* Mission = MakeBriefingMission(2.f);
	TestNotNull(TEXT("Mission definition is created"), Mission);
	if (!Mission)
	{
		return false;
	}

	TestTrue(
		TEXT("ConfigureFromMission accepts authored briefing copy"),
		Briefing->ConfigureFromMission(Mission));
	TestEqual(
		TEXT("ConfigureFromMission enters Warming"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Warming);
	TestEqual(
		TEXT("Warmup is taken from the mission definition"),
		Briefing->GetMinimumWarmupSeconds(),
		2.f);
	TestFalse(TEXT("Warming briefing cannot launch"), Briefing->CanLaunch());

	Briefing->SetAssetsReady(true);
	TestEqual(
		TEXT("SetAssetsReady(true) without elapsed warmup stays Warming"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Warming);
	TestFalse(
		TEXT("Assets ready does not bypass minimum warmup"),
		Briefing->CanLaunch());
	TestFalse(
		TEXT("AcknowledgeAndLaunch is rejected when only assets are ready"),
		Briefing->AcknowledgeAndLaunch());

	Briefing->AdvanceBriefing(1.9f);
	TestEqual(
		TEXT("Partial warmup stays Warming"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Warming);
	TestFalse(TEXT("Partial warmup cannot launch"), Briefing->CanLaunch());

	Briefing->SetAssetsReady(false);
	Briefing->AdvanceBriefing(0.2f);
	TestTrue(
		TEXT("Elapsed warmup meets the authored minimum"),
		Briefing->GetElapsedSeconds() >= Briefing->GetMinimumWarmupSeconds());
	TestEqual(
		TEXT("Elapsed warmup without SetAssetsReady(true) stays Warming"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Warming);
	TestFalse(
		TEXT("Warmup without assets ready cannot launch"),
		Briefing->CanLaunch());
	TestFalse(
		TEXT("AcknowledgeAndLaunch is rejected when only warmup has elapsed"),
		Briefing->AcknowledgeAndLaunch());

	Briefing->SetAssetsReady(true);
	TestEqual(
		TEXT("Warmup and SetAssetsReady(true) enter Ready"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Ready);
	TestTrue(TEXT("Ready briefing can launch"), Briefing->CanLaunch());

	TestTrue(
		TEXT("AcknowledgeAndLaunch succeeds from Ready"),
		Briefing->AcknowledgeAndLaunch());
	TestEqual(
		TEXT("AcknowledgeAndLaunch records Launched"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Launched);
	TestTrue(
		TEXT("Launched briefing still reports CanLaunch"),
		Briefing->CanLaunch());
	return true;
}

#endif
