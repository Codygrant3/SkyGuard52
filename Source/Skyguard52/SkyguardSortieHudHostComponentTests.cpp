#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardSortieHudHostComponent.h"

#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSortieHudHostComponentShouldShowDebriefForEveryStateTest,
	"Skyguard52.Presentation.Sortie.HudHost.ShouldShowDebriefForEveryState",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortieHudHostComponentShouldShowDebriefForEveryStateTest::RunTest(
	const FString& Parameters)
{
	// Every ESkyguardSortiePresentationState from
	// SkyguardSortiePresentationComponent.h. Debrief shows only on the
	// terminal success/fail states after a sortie.
	TestFalse(
		TEXT("Unconfigured is not a debrief state"),
		USkyguardSortieHudHostComponent::ShouldShowDebriefForState(
			ESkyguardSortiePresentationState::Unconfigured));
	TestFalse(
		TEXT("Briefing is not a debrief state"),
		USkyguardSortieHudHostComponent::ShouldShowDebriefForState(
			ESkyguardSortiePresentationState::Briefing));
	TestFalse(
		TEXT("SortieActive is not a debrief state"),
		USkyguardSortieHudHostComponent::ShouldShowDebriefForState(
			ESkyguardSortiePresentationState::SortieActive));
	TestTrue(
		TEXT("DebriefReady is a terminal success debrief state"),
		USkyguardSortieHudHostComponent::ShouldShowDebriefForState(
			ESkyguardSortiePresentationState::DebriefReady));
	TestTrue(
		TEXT("SaveFailure is a terminal fail debrief state"),
		USkyguardSortieHudHostComponent::ShouldShowDebriefForState(
			ESkyguardSortiePresentationState::SaveFailure));
	TestTrue(
		TEXT("TravelReady is a terminal success debrief state"),
		USkyguardSortieHudHostComponent::ShouldShowDebriefForState(
			ESkyguardSortiePresentationState::TravelReady));
	TestTrue(
		TEXT("TravelBlocked is a terminal fail debrief state"),
		USkyguardSortieHudHostComponent::ShouldShowDebriefForState(
			ESkyguardSortiePresentationState::TravelBlocked));
	TestTrue(
		TEXT("CampaignComplete is a terminal success debrief state"),
		USkyguardSortieHudHostComponent::ShouldShowDebriefForState(
			ESkyguardSortiePresentationState::CampaignComplete));

	TestEqual(
		TEXT("ESkyguardSortiePresentationState still ends at CampaignComplete"),
		static_cast<uint8>(ESkyguardSortiePresentationState::CampaignComplete),
		static_cast<uint8>(7));
	return true;
}

#endif
