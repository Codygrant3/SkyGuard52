#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardSortieHudHostComponent.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardSortieHudHostComponentTests.cpp.
// Remaining NewObject / nullptr-bind public API only. Existing
// SkyguardSortieHudHostComponentTests.cpp already covers
// ShouldShowDebriefForState for every ESkyguardSortiePresentationState.
// NewObject only: no Gunner / Yak / Igla / rifle spawn, no widget or
// world spawn.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSortieHudHostFailClosedTest,
	"Skyguard52.Presentation.Sortie.HudHost.FailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortieHudHostFailClosedTest::RunTest(const FString& Parameters)
{
	USkyguardSortieHudHostComponent* Host =
		NewObject<USkyguardSortieHudHostComponent>(GetTransientPackage());
	TestNotNull(TEXT("NewObject HUD host constructs"), Host);
	if (!Host)
	{
		return false;
	}

	TestNull(
		TEXT("NewObject default GetBoundPresentation is nullptr"),
		Host->GetBoundPresentation());
	TestEqual(
		TEXT("NewObject default BriefingZOrder is 50"),
		Host->BriefingZOrder,
		50);
	TestEqual(
		TEXT("NewObject default DebriefZOrder is 60"),
		Host->DebriefZOrder,
		60);
	TestFalse(
		TEXT("Constructor disables PrimaryComponentTick"),
		Host->PrimaryComponentTick.bCanEverTick);

	Host->BindPresentation(nullptr);
	TestNull(
		TEXT("BindPresentation(nullptr) leaves GetBoundPresentation nullptr"),
		Host->GetBoundPresentation());

	Host->RefreshFromPresentationState();
	TestNull(
		TEXT("RefreshFromPresentationState with no presentation does not bind"),
		Host->GetBoundPresentation());

	TestNull(
		TEXT("NewObject HUD host has no world for FindPresentationInWorld"),
		Host->GetWorld());
	Host->RebindIfNeeded();
	TestNull(
		TEXT("RebindIfNeeded without a world leaves presentation nullptr"),
		Host->GetBoundPresentation());

	USkyguardSortiePresentationComponent* Presentation =
		NewObject<USkyguardSortiePresentationComponent>(GetTransientPackage());
	TestNotNull(TEXT("NewObject presentation constructs"), Presentation);
	if (!Presentation)
	{
		return false;
	}

	Host->BindPresentation(Presentation);
	TestTrue(
		TEXT("BindPresentation binds the NewObject presentation"),
		Host->GetBoundPresentation() == Presentation);

	Host->BindPresentation(Presentation);
	TestTrue(
		TEXT("BindPresentation of the same pointer is a no-op"),
		Host->GetBoundPresentation() == Presentation);

	Host->BindPresentation(nullptr);
	TestNull(
		TEXT("BindPresentation(nullptr) unbinds the presentation"),
		Host->GetBoundPresentation());

	return true;
}

#endif
