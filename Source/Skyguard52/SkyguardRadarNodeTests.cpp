#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardRadarNode.h"

#include "SkyguardRuntimeMeshCatalog.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardRadarNodeTests
{
	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardRadarNodeTestWorld"));
			check(World);
			FWorldContext& Context =
				GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}
		~FWorldScope()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
		}
		UWorld* Get() const { return World; }
	private:
		UWorld* World = nullptr;
	};

	bool SlotPreferredEmpty(const FName SlotId)
	{
		for (const FSkyguardMeshBindSlot& Slot :
			USkyguardRuntimeMeshCatalog::GetCodeDefaultSlots())
		{
			if (Slot.SlotId == SlotId)
			{
				return Slot.Preferred.IsNull();
			}
		}
		return true;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadarNodeCatalogPreferredEmptyTest,
	"Skyguard52.RadarNode.Catalog.PreferredEmptyForVanAndDish",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadarNodeCatalogPreferredEmptyTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardRadarNodeTests;
	TestTrue(
		TEXT("Radar.Van Preferred stays empty"),
		SlotPreferredEmpty(TEXT("Radar.Van")));
	TestTrue(
		TEXT("Radar.Dish Preferred stays empty"),
		SlotPreferredEmpty(TEXT("Radar.Dish")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadarNodeBindWithoutMeshDoesNotCrashTest,
	"Skyguard52.RadarNode.Presentation.BindDoesNotCrashWithoutMesh",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadarNodeBindWithoutMeshDoesNotCrashTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardRadarNodeTests;
	FWorldScope Scope;
	ASkyguardRadarNode* Radar = Scope.Get()->SpawnActor<ASkyguardRadarNode>();
	TestNotNull(TEXT("RadarNode spawns"), Radar);
	if (!Radar)
	{
		return false;
	}

	TestNotNull(TEXT("Body component exists"), Radar->GetBody());
	TestNotNull(TEXT("Dish component exists"), Radar->GetDish());
	TestTrue(
		TEXT("CDO ctor does not bind a van mesh"),
		Radar->GetBody() && Radar->GetBody()->GetStaticMesh() == nullptr);
	TestTrue(
		TEXT("CDO ctor does not bind a dish mesh"),
		Radar->GetDish() && Radar->GetDish()->GetStaticMesh() == nullptr);

	FSkyguardMeshBindSlot EmptySlot;
	EmptySlot.SlotId = TEXT("Radar.Van");
	TestNull(
		TEXT("Empty Preferred and ProxyFallback resolve to no mesh"),
		USkyguardRuntimeMeshCatalog::ResolveSlot(EmptySlot));

	Radar->BindPresentation();

	if (Radar->GetBody())
	{
		Radar->GetBody()->SetStaticMesh(nullptr);
	}
	if (Radar->GetDish())
	{
		Radar->GetDish()->SetStaticMesh(nullptr);
	}
	Radar->BindPresentation();
	TestTrue(TEXT("BindPresentation is safe without a preassigned mesh"), true);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadarNodePresentationEnableDisableTest,
	"Skyguard52.RadarNode.Presentation.CanEnableAndDisable",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadarNodePresentationEnableDisableTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardRadarNodeTests;
	FWorldScope Scope;
	ASkyguardRadarNode* Radar = Scope.Get()->SpawnActor<ASkyguardRadarNode>();
	TestNotNull(TEXT("RadarNode spawns"), Radar);
	if (!Radar || !Radar->GetBody() || !Radar->GetDish())
	{
		return false;
	}

	Radar->BindPresentation();
	TestTrue(TEXT("presentation starts enabled"), Radar->IsPresentationEnabled());
	TestTrue(TEXT("van visible when enabled"), Radar->GetBody()->IsVisible());
	TestTrue(TEXT("dish visible when enabled"), Radar->GetDish()->IsVisible());

	const float DishYawBefore = Radar->GetDish()->GetRelativeRotation().Yaw;
	Radar->Tick(0.5f);
	TestTrue(
		TEXT("dish spins while presentation is enabled"),
		!FMath::IsNearlyEqual(
			Radar->GetDish()->GetRelativeRotation().Yaw, DishYawBefore, 0.01f));

	Radar->SetPresentationEnabled(false);
	TestFalse(TEXT("presentation reports disabled"), Radar->IsPresentationEnabled());
	TestFalse(TEXT("van hidden when disabled"), Radar->GetBody()->IsVisible());
	TestFalse(TEXT("dish hidden when disabled"), Radar->GetDish()->IsVisible());

	const float DishYawDisabled = Radar->GetDish()->GetRelativeRotation().Yaw;
	Radar->Tick(0.5f);
	TestTrue(
		TEXT("dish does not spin while presentation is disabled"),
		FMath::IsNearlyEqual(
			Radar->GetDish()->GetRelativeRotation().Yaw, DishYawDisabled, 0.01f));

	Radar->SetPresentationEnabled(true);
	TestTrue(TEXT("presentation reports enabled"), Radar->IsPresentationEnabled());
	TestTrue(TEXT("van shown when re-enabled"), Radar->GetBody()->IsVisible());
	TestTrue(TEXT("dish shown when re-enabled"), Radar->GetDish()->IsVisible());
	return true;
}

#endif
