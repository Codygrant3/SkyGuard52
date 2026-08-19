#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardPatrolShipBoss.h"
#include "SkyguardRuntimeMeshCatalog.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardPatrolShipPresentationTests
{
	bool PathLooksLikeHarborKit(const FSoftObjectPath& Path)
	{
		if (!Path.IsValid())
		{
			return false;
		}
		const FString Text = Path.ToString();
		return Text.Contains(TEXT("Harbor"), ESearchCase::IgnoreCase);
	}

	bool PathLooksLikeAuthoredCatalogMesh(const FSoftObjectPath& Path)
	{
		if (!Path.IsValid())
		{
			return false;
		}
		const FString Text = Path.ToString();
		return Text.Contains(TEXT("/Game/Skyguard/"), ESearchCase::IgnoreCase);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPatrolShipPreferredSlotsStayEmptyTest,
	"Skyguard52.MeshBind.PatrolShip.PreferredSlotsStayEmpty",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPatrolShipPreferredSlotsStayEmptyTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardPatrolShipPresentationTests;

	const FSkyguardMeshBindSlot HullSlot =
		ASkyguardPatrolShipBoss::MakeHullBindSlot();
	TestEqual(
		TEXT("hull slot id"),
		HullSlot.SlotId,
		FName(TEXT("PatrolShip.Hull")));
	TestTrue(
		TEXT("hull Preferred stays empty"),
		HullSlot.Preferred.IsNull());
	TestFalse(
		TEXT("hull ProxyFallback is set"),
		HullSlot.ProxyFallback.IsNull());
	TestTrue(
		TEXT("hull ProxyFallback is the engine Cube primitive"),
		HullSlot.ProxyFallback.ToSoftObjectPath().ToString().Contains(
			TEXT("/Engine/BasicShapes/Cube")));
	TestFalse(
		TEXT("hull ProxyFallback is not a Harbor kit path"),
		PathLooksLikeHarborKit(HullSlot.ProxyFallback.ToSoftObjectPath()));
	TestFalse(
		TEXT("hull ProxyFallback is not an authored catalog mesh"),
		PathLooksLikeAuthoredCatalogMesh(HullSlot.ProxyFallback.ToSoftObjectPath()));

	TestTrue(
		TEXT("catalog has no authored PatrolShip.Hull Preferred slot"),
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(
			TEXT("PatrolShip.Hull")) == nullptr);

	for (const FSkyguardMeshBindSlot& Slot :
		USkyguardRuntimeMeshCatalog::GetCodeDefaultSlots())
	{
		TestFalse(
			*FString::Printf(
				TEXT("catalog slot '%s' Preferred is not a Harbor kit fill"),
				*Slot.SlotId.ToString()),
			PathLooksLikeHarborKit(Slot.Preferred.ToSoftObjectPath()));
		if (Slot.SlotId.ToString().Contains(TEXT("PatrolShip")))
		{
			TestTrue(
				*FString::Printf(
					TEXT("PatrolShip catalog slot '%s' Preferred stays empty"),
					*Slot.SlotId.ToString()),
				Slot.Preferred.IsNull());
		}
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPatrolShipBindsProxyFallbackWithoutCatalogMeshTest,
	"Skyguard52.MeshBind.PatrolShip.BindsProxyFallbackWithoutCatalogMesh",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPatrolShipBindsProxyFallbackWithoutCatalogMeshTest::RunTest(
	const FString& Parameters)
{
	const ASkyguardPatrolShipBoss* CDO = GetDefault<ASkyguardPatrolShipBoss>();
	TestNotNull(TEXT("PatrolShip CDO exists"), CDO);
	if (!CDO || !CDO->GetHull())
	{
		return false;
	}
	TestTrue(
		TEXT("CDO constructor does not bind a hull mesh"),
		CDO->GetHull()->GetStaticMesh() == nullptr);

	ASkyguardPatrolShipBoss* Constructed = NewObject<ASkyguardPatrolShipBoss>();
	TestNotNull(TEXT("PatrolShip constructs"), Constructed);
	if (!Constructed || !Constructed->GetHull())
	{
		return false;
	}
	TestTrue(
		TEXT("instance constructor does not bind a hull mesh"),
		Constructed->GetHull()->GetStaticMesh() == nullptr);

	TestTrue(
		TEXT("catalog Preferred/default slot is empty so bind uses ProxyFallback"),
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(
			TEXT("PatrolShip.Hull")) == nullptr);

	Constructed->BindPresentation();
	TestNotNull(
		TEXT("BindPresentation without a catalog mesh does not crash and binds a hull"),
		Constructed->GetHull()->GetStaticMesh());
	if (Constructed->GetHull()->GetStaticMesh())
	{
		TestEqual(
			TEXT("ProxyFallback engine Cube is used when no catalog hull exists"),
			Constructed->GetHull()->GetStaticMesh()->GetName(),
			FString(TEXT("Cube")));
	}

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardPatrolShipBindWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}
	ASkyguardPatrolShipBoss* Spawned =
		World->SpawnActor<ASkyguardPatrolShipBoss>();
	TestNotNull(TEXT("spawned PatrolShip"), Spawned);
	if (!Spawned || !Spawned->GetHull())
	{
		World->DestroyWorld(false);
		return false;
	}
	TestTrue(
		TEXT("spawned constructor still has no hull mesh before BeginPlay"),
		Spawned->GetHull()->GetStaticMesh() == nullptr);
	Spawned->DispatchBeginPlay();
	TestNotNull(
		TEXT("BeginPlay binds hull via ProxyFallback without a catalog mesh"),
		Spawned->GetHull()->GetStaticMesh());
	World->DestroyWorld(false);
	return true;
}

#endif
