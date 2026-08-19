#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardDrone.h"
#include "SkyguardRuntimeMeshCatalog.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardDroneMeshBindTests
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

	bool IsDroneCatalogSlot(const FName SlotId)
	{
		return SlotId == TEXT("Drone.Body") ||
			SlotId == TEXT("Drone.HeavyBody") ||
			SlotId == TEXT("Drone.Hull");
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardDronePreferredSlotsStayEmptyTest,
	"Skyguard52.MeshBind.Drone.PreferredSlotsStayEmpty",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDronePreferredSlotsStayEmptyTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardDroneMeshBindTests;

	const FSkyguardMeshBindSlot HullSlot = ASkyguardDrone::MakeHullBindSlot();
	TestEqual(
		TEXT("hull slot id"),
		HullSlot.SlotId,
		FName(TEXT("Drone.Hull")));
	TestTrue(
		TEXT("hull Preferred stays empty"),
		HullSlot.Preferred.IsNull());
	TestFalse(
		TEXT("hull ProxyFallback is set"),
		HullSlot.ProxyFallback.IsNull());
	TestTrue(
		TEXT("hull ProxyFallback is an engine Cube or Sphere primitive"),
		HullSlot.ProxyFallback.ToSoftObjectPath().ToString().Contains(
			TEXT("/Engine/BasicShapes/Cube")) ||
		HullSlot.ProxyFallback.ToSoftObjectPath().ToString().Contains(
			TEXT("/Engine/BasicShapes/Sphere")));
	TestFalse(
		TEXT("hull ProxyFallback is not a Harbor kit path"),
		PathLooksLikeHarborKit(HullSlot.ProxyFallback.ToSoftObjectPath()));
	TestFalse(
		TEXT("hull ProxyFallback is not an authored catalog mesh"),
		PathLooksLikeAuthoredCatalogMesh(HullSlot.ProxyFallback.ToSoftObjectPath()));

	bool bSawDroneBody = false;
	bool bSawDroneHeavyBody = false;
	for (const FSkyguardMeshBindSlot& Slot :
		USkyguardRuntimeMeshCatalog::GetCodeDefaultSlots())
	{
		if (IsDroneCatalogSlot(Slot.SlotId))
		{
			TestTrue(
				*FString::Printf(
					TEXT("catalog drone slot '%s' Preferred stays empty"),
					*Slot.SlotId.ToString()),
				Slot.Preferred.IsNull());
		}
		if (Slot.SlotId == TEXT("Drone.Body"))
		{
			bSawDroneBody = true;
		}
		if (Slot.SlotId == TEXT("Drone.HeavyBody"))
		{
			bSawDroneHeavyBody = true;
		}
		TestFalse(
			*FString::Printf(
				TEXT("catalog slot '%s' Preferred is not a Harbor kit fill"),
				*Slot.SlotId.ToString()),
			PathLooksLikeHarborKit(Slot.Preferred.ToSoftObjectPath()));
	}
	TestTrue(TEXT("Drone.Body remains a catalog slot"), bSawDroneBody);
	TestTrue(
		TEXT("Drone.HeavyBody remains a catalog slot"),
		bSawDroneHeavyBody);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardDroneBindsProxyFallbackWithoutAuthoredMeshTest,
	"Skyguard52.MeshBind.Drone.BindsProxyFallbackWithoutAuthoredMesh",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDroneBindsProxyFallbackWithoutAuthoredMeshTest::RunTest(
	const FString& Parameters)
{
	const ASkyguardDrone* CDO = GetDefault<ASkyguardDrone>();
	TestNotNull(TEXT("Drone CDO exists"), CDO);
	if (!CDO || !CDO->GetHull())
	{
		return false;
	}
	TestTrue(
		TEXT("CDO constructor does not bind an authored hull mesh"),
		CDO->GetHull()->GetStaticMesh() == nullptr);

	ASkyguardDrone* Constructed = NewObject<ASkyguardDrone>();
	TestNotNull(TEXT("Drone constructs"), Constructed);
	if (!Constructed || !Constructed->GetHull())
	{
		return false;
	}
	TestTrue(
		TEXT("instance constructor does not bind an authored hull mesh"),
		Constructed->GetHull()->GetStaticMesh() == nullptr);

	Constructed->BindHull();
	TestNotNull(
		TEXT("BindHull without authored mesh does not crash and binds a hull"),
		Constructed->GetHull()->GetStaticMesh());
	if (Constructed->GetHull()->GetStaticMesh())
	{
		const FString BoundName = Constructed->GetHull()->GetStaticMesh()->GetName();
		TestTrue(
			TEXT("ProxyFallback engine Cube or Sphere is used when no authored hull exists"),
			BoundName == TEXT("Cube") || BoundName == TEXT("Sphere"));
	}

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardDroneMeshBindWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}
	ASkyguardDrone* Spawned = World->SpawnActor<ASkyguardDrone>();
	TestNotNull(TEXT("spawned Drone"), Spawned);
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
		TEXT("BeginPlay binds hull via ProxyFallback without crashing"),
		Spawned->GetHull()->GetStaticMesh());
	World->DestroyWorld(false);
	return true;
}

#endif
