#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardSortiePresentationComponent.h"

#include "SkyguardMissionDefinition.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardSortiePresentationTests.cpp.
// Fail-closed public API only: NewObject, no Gunner spawn, no
// BindGunshipDirector, no campaign save.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSortiePresentationFailClosedPublicApiTest,
	"Skyguard52.Presentation.Sortie.FailClosedPublicApi",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortiePresentationFailClosedPublicApiTest::RunTest(
	const FString& Parameters)
{
	USkyguardSortiePresentationComponent* Presentation =
		NewObject<USkyguardSortiePresentationComponent>(
			GetTransientPackage());
	TestNotNull(TEXT("NewObject presentation constructs"), Presentation);
	if (!Presentation)
	{
		return false;
	}

	TestEqual(
		TEXT("NewObject default GetPresentationState is Unconfigured"),
		Presentation->GetPresentationState(),
		ESkyguardSortiePresentationState::Unconfigured);
	TestFalse(
		TEXT("NewObject default IsConfigured is false"),
		Presentation->IsConfigured());
	TestFalse(
		TEXT("NewObject default HasCpgDebrief is false"),
		Presentation->HasCpgDebrief());
	TestEqual(
		TEXT("HowToFly rows stay empty while Unconfigured"),
		Presentation->GetHowToFlyRows().Num(),
		0);
	TestEqual(
		TEXT("Briefing cards stay empty while Unconfigured"),
		Presentation->GetBriefingCards().Num(),
		0);

	TestFalse(
		TEXT("ConfigureFromMission(nullptr) is fail-closed"),
		Presentation->ConfigureFromMission(nullptr));
	TestEqual(
		TEXT("Failed nullptr configure leaves Unconfigured"),
		Presentation->GetPresentationState(),
		ESkyguardSortiePresentationState::Unconfigured);
	TestFalse(
		TEXT("Failed nullptr configure leaves IsConfigured false"),
		Presentation->IsConfigured());

	TestFalse(
		TEXT("LaunchSortie is fail-closed after a failed configure"),
		Presentation->LaunchSortie());
	TestFalse(
		TEXT("AcknowledgeBriefing is fail-closed after a failed configure"),
		Presentation->AcknowledgeBriefing());
	TestFalse(
		TEXT("AcknowledgeDebrief is fail-closed after a failed configure"),
		Presentation->AcknowledgeDebrief());
	TestFalse(
		TEXT("ContinueSortie is fail-closed with no director (AcknowledgeDebrief)"),
		Presentation->ContinueSortie());
	TestFalse(
		TEXT("RequestNextMissionTravel(nullptr) is fail-closed after a failed configure"),
		Presentation->RequestNextMissionTravel(nullptr));

	TestFalse(
		TEXT("SelectLoadoutSlot(0) is fail-closed"),
		Presentation->SelectLoadoutSlot(0));
	TestFalse(
		TEXT("SelectLoadoutSlot(5) is fail-closed"),
		Presentation->SelectLoadoutSlot(5));
	TestFalse(
		TEXT("Rejected slots leave HasCpgDebrief false"),
		Presentation->HasCpgDebrief());
	TestTrue(
		TEXT("SelectLoadoutSlot(1) succeeds without a Gunner"),
		Presentation->SelectLoadoutSlot(1));
	TestEqual(
		TEXT("SelectLoadoutSlot(1) sets AntiArmor"),
		Presentation->GetSelectedLoadout(),
		ESkyguardLoadout::AntiArmor);
	TestTrue(
		TEXT("SelectLoadoutSlot(1) sets HasCpgDebrief without a Gunner"),
		Presentation->HasCpgDebrief());
	TestEqual(
		TEXT("Loadout select leaves presentation Unconfigured"),
		Presentation->GetPresentationState(),
		ESkyguardSortiePresentationState::Unconfigured);
	TestEqual(
		TEXT("HowToFly rows stay empty while still Unconfigured"),
		Presentation->GetHowToFlyRows().Num(),
		0);
	TestEqual(
		TEXT("Briefing cards stay empty while still Unconfigured"),
		Presentation->GetBriefingCards().Num(),
		0);

	USkyguardSortiePresentationComponent* EmptyMissionPresentation =
		NewObject<USkyguardSortiePresentationComponent>(
			GetTransientPackage());
	USkyguardMissionDefinition* EmptyMission =
		NewObject<USkyguardMissionDefinition>(GetTransientPackage());
	TestNotNull(
		TEXT("Empty-mission presentation constructs"),
		EmptyMissionPresentation);
	TestNotNull(TEXT("Empty NewObject mission constructs"), EmptyMission);
	if (!EmptyMissionPresentation || !EmptyMission)
	{
		return false;
	}

	TestTrue(
		TEXT("NewObject mission default MissionId is none"),
		EmptyMission->MissionId.IsNone());
	TestTrue(
		TEXT("NewObject mission default DisplayName is empty"),
		EmptyMission->DisplayName.IsEmpty());
	TestTrue(
		TEXT("NewObject mission default Presentation.Briefing is empty"),
		EmptyMission->Presentation.Briefing.IsEmpty());
	TestFalse(
		TEXT("ConfigureFromMission requires MissionId, DisplayName, and Briefing"),
		EmptyMissionPresentation->ConfigureFromMission(EmptyMission));
	TestEqual(
		TEXT("Empty-mission configure leaves Unconfigured"),
		EmptyMissionPresentation->GetPresentationState(),
		ESkyguardSortiePresentationState::Unconfigured);
	TestEqual(
		TEXT("HowToFly rows stay empty after a rejected empty mission"),
		EmptyMissionPresentation->GetHowToFlyRows().Num(),
		0);
	TestEqual(
		TEXT("Briefing cards stay empty after a rejected empty mission"),
		EmptyMissionPresentation->GetBriefingCards().Num(),
		0);

	return true;
}

#endif
