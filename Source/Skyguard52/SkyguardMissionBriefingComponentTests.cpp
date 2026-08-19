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
			TEXT("CPG hold. Prioritize the threat that can kill the helicopter."));
		Mission->Presentation.MinimumBriefingWarmupSeconds = WarmupSeconds;
		return Mission;
	}

	USkyguardMissionBriefingComponent* MakeBriefing()
	{
		return NewObject<USkyguardMissionBriefingComponent>(GetTransientPackage());
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionBriefingLaunchGateTest,
	"Skyguard52.Briefing.LaunchGateRequiresWarmupAndAssetsReady",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionBriefingLaunchGateTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardMissionBriefingComponentTests;

	USkyguardMissionBriefingComponent* Briefing = MakeBriefing();
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
	Briefing->AdvanceBriefing(1.9f);
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

	USkyguardMissionBriefingComponent* WarmupOnly = MakeBriefing();
	TestNotNull(TEXT("Second briefing component is created"), WarmupOnly);
	if (!WarmupOnly)
	{
		return false;
	}
	TestTrue(
		TEXT("Second briefing configures from the same mission"),
		WarmupOnly->ConfigureFromMission(Mission));
	WarmupOnly->AdvanceBriefing(WarmupOnly->GetMinimumWarmupSeconds());
	TestTrue(
		TEXT("Elapsed warmup meets the authored minimum"),
		WarmupOnly->GetElapsedSeconds() >= WarmupOnly->GetMinimumWarmupSeconds());
	TestEqual(
		TEXT("Elapsed warmup without SetAssetsReady(true) stays Warming"),
		WarmupOnly->GetBriefingState(),
		ESkyguardMissionBriefingState::Warming);
	TestFalse(
		TEXT("Warmup without assets ready cannot launch"),
		WarmupOnly->CanLaunch());
	TestFalse(
		TEXT("AcknowledgeAndLaunch is rejected when only warmup has elapsed"),
		WarmupOnly->AcknowledgeAndLaunch());

	Briefing->AdvanceBriefing(0.2f);
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

	WarmupOnly->SetAssetsReady(true);
	TestEqual(
		TEXT("Warmup-first briefing becomes Ready after SetAssetsReady(true)"),
		WarmupOnly->GetBriefingState(),
		ESkyguardMissionBriefingState::Ready);
	TestTrue(
		TEXT("Warmup-first briefing can launch after assets ready"),
		WarmupOnly->CanLaunch());
	TestTrue(
		TEXT("Warmup-first briefing acknowledges and launches"),
		WarmupOnly->AcknowledgeAndLaunch());
	TestEqual(
		TEXT("Warmup-first briefing records Launched"),
		WarmupOnly->GetBriefingState(),
		ESkyguardMissionBriefingState::Launched);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionBriefingUnconfiguredStaysBlockedTest,
	"Skyguard52.Briefing.UnconfiguredRejectsAdvanceAndEmptyMission",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionBriefingUnconfiguredStaysBlockedTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMissionBriefingComponentTests;

	USkyguardMissionBriefingComponent* Briefing = MakeBriefing();
	TestNotNull(TEXT("Briefing component is created"), Briefing);
	if (!Briefing)
	{
		return false;
	}

	Briefing->AdvanceBriefing(5.f);
	Briefing->SetAssetsReady(true);
	TestEqual(
		TEXT("AdvanceBriefing is ignored while Unconfigured"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Unconfigured);
	TestEqual(
		TEXT("Unconfigured elapsed time stays zero"),
		Briefing->GetElapsedSeconds(),
		0.f);
	TestFalse(TEXT("Unconfigured still cannot launch"), Briefing->CanLaunch());

	TestFalse(
		TEXT("ConfigureFromMission rejects a null mission"),
		Briefing->ConfigureFromMission(nullptr));
	TestEqual(
		TEXT("Null mission leaves briefing Unconfigured"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Unconfigured);

	USkyguardMissionDefinition* EmptyBriefing =
		NewObject<USkyguardMissionDefinition>(GetTransientPackage());
	EmptyBriefing->Presentation.MinimumBriefingWarmupSeconds = 1.f;
	TestFalse(
		TEXT("ConfigureFromMission rejects an empty briefing"),
		Briefing->ConfigureFromMission(EmptyBriefing));
	TestEqual(
		TEXT("Empty briefing leaves state Unconfigured"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Unconfigured);
	return true;
}

#endif
