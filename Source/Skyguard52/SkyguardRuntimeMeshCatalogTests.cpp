#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardRuntimeMeshCatalog.h"
#include "SkyguardSortiePresentationComponent.h"
#include "SkyguardSortiePresentationWidgets.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardMissionDefinition.h"
#include "Engine/StaticMesh.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRuntimeMeshCatalogPrefersPreferredTest,
	"Skyguard52.MeshBind.Catalog.ResolvePrefersPreferredWhenSet",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRuntimeMeshCatalogPrefersPreferredTest::RunTest(
	const FString& Parameters)
{
	USkyguardRuntimeMeshCatalog* Catalog =
		NewObject<USkyguardRuntimeMeshCatalog>();
	Catalog->EnsureDefaultSlots();
	TestTrue(
		TEXT("Code defaults seed Gunner.Rifle"),
		Catalog->FindSlot(TEXT("Gunner.Rifle")) != nullptr);

	FSkyguardMeshBindSlot Slot;
	Slot.SlotId = TEXT("Test.PreferredWins");
	Slot.Preferred = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(
		TEXT("/Engine/BasicShapes/Cube.Cube")));
	Slot.ProxyFallback = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(
		TEXT("/Engine/BasicShapes/Sphere.Sphere")));
	Slot.Notes = TEXT("Automation preference check");

	UStaticMesh* Resolved = USkyguardRuntimeMeshCatalog::ResolveSlot(Slot);
	TestNotNull(TEXT("ResolveSlot loads a mesh"), Resolved);
	if (Resolved)
	{
		TestTrue(
			TEXT("Preferred Cube wins over ProxyFallback Sphere"),
			Resolved->GetName() == TEXT("Cube"));
	}

	FSkyguardMeshBindSlot ProxyOnly;
	ProxyOnly.SlotId = TEXT("Test.ProxyOnly");
	ProxyOnly.ProxyFallback = TSoftObjectPtr<UStaticMesh>(FSoftObjectPath(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));
	UStaticMesh* ProxyResolved =
		USkyguardRuntimeMeshCatalog::ResolveSlot(ProxyOnly);
	TestNotNull(TEXT("Empty Preferred falls through to ProxyFallback"), ProxyResolved);
	if (ProxyResolved)
	{
		TestTrue(
			TEXT("ProxyFallback Cylinder is used when Preferred empty"),
			ProxyResolved->GetName() == TEXT("Cylinder"));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardBriefingWidgetConfigureSmokeTest,
	"Skyguard52.Presentation.UMG.BriefingWidgetConfiguresWithoutCrash",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardBriefingWidgetConfigureSmokeTest::RunTest(
	const FString& Parameters)
{
	USkyguardBriefingWidget* Widget =
		NewObject<USkyguardBriefingWidget>(GetTransientPackage());
	TestNotNull(TEXT("Briefing widget constructs"), Widget);
	if (!Widget)
	{
		return false;
	}

	// Null presentation must be safe.
	Widget->Configure(nullptr);
	TestTrue(
		TEXT("Null presentation yields empty title"),
		Widget->GetMissionTitle().IsEmpty());
	TestFalse(
		TEXT("AcknowledgeBriefing is fail-closed without presentation"),
		Widget->AcknowledgeBriefing());
	TestFalse(
		TEXT("LaunchSortie is fail-closed without presentation"),
		Widget->LaunchSortie());

	USkyguardCampaignDefinition* Campaign =
		LoadObject<USkyguardCampaignDefinition>(
			nullptr,
			TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Campaign_Skyguard52.DA_Campaign_Skyguard52"));
	if (!Campaign)
	{
		AddWarning(TEXT("Campaign asset unavailable; null-path smoke still passed."));
		return true;
	}
	USkyguardMissionDefinition* Mission =
		Campaign->FindMission(TEXT("M01_CoastalIntercept"));
	if (!Mission)
	{
		AddWarning(TEXT("Mission 1 unavailable; null-path smoke still passed."));
		return true;
	}

	USkyguardSortiePresentationComponent* Presentation =
		NewObject<USkyguardSortiePresentationComponent>(GetTransientPackage());
	TestTrue(
		TEXT("Presentation configures from Mission 1"),
		Presentation->ConfigureFromMission(Mission));
	Widget->Configure(Presentation);
	TestTrue(
		TEXT("Mission title binds through widget"),
		Widget->GetMissionTitle().EqualTo(Mission->DisplayName));
	TestTrue(
		TEXT("Briefing cards bind through widget"),
		Widget->GetBriefingCards().Num() > 0);
	TestTrue(
		TEXT("AcknowledgeBriefing succeeds in Briefing state"),
		Widget->AcknowledgeBriefing());
	return true;
}

#endif
