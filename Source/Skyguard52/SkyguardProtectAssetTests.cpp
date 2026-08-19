#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardProtectAsset.h"
#include "SkyguardRuntimeMeshCatalog.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardProtectAssetTests
{
	bool SlotIdLooksLikeHarborKitFill(const FName SlotId)
	{
		const FString Id = SlotId.ToString();
		return Id.Contains(TEXT("Harbor"), ESearchCase::IgnoreCase) ||
			Id.Contains(TEXT("Ship"), ESearchCase::IgnoreCase) ||
			Id.Contains(TEXT("Boat"), ESearchCase::IgnoreCase) ||
			Id.Contains(TEXT("Truck"), ESearchCase::IgnoreCase);
	}

	bool PathLooksLikeHarborKit(const FSoftObjectPath& Path)
	{
		if (!Path.IsValid())
		{
			return false;
		}
		const FString Text = Path.ToString();
		return Text.Contains(TEXT("Harbor"), ESearchCase::IgnoreCase);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardProtectAssetBindsCargoHullWithoutAuthoredMeshTest,
	"Skyguard52.MeshBind.ProtectAsset.BindsCargoHullWithoutAuthoredMesh",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardProtectAssetBindsCargoHullWithoutAuthoredMeshTest::RunTest(
	const FString& Parameters)
{
	const ASkyguardProtectAsset* CDO = GetDefault<ASkyguardProtectAsset>();
	TestNotNull(TEXT("ProtectAsset CDO exists"), CDO);
	if (!CDO || !CDO->GetHull())
	{
		return false;
	}
	TestTrue(
		TEXT("CDO constructor does not bind a cargo hull mesh"),
		CDO->GetHull()->GetStaticMesh() == nullptr);

	ASkyguardProtectAsset* Constructed = NewObject<ASkyguardProtectAsset>();
	TestNotNull(TEXT("ProtectAsset constructs"), Constructed);
	if (!Constructed || !Constructed->GetHull())
	{
		return false;
	}
	TestTrue(
		TEXT("instance constructor does not bind a cargo hull mesh"),
		Constructed->GetHull()->GetStaticMesh() == nullptr);

	TestTrue(
		TEXT("catalog has no authored ProtectAsset.CargoHull Preferred slot"),
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(
			TEXT("ProtectAsset.CargoHull")) == nullptr);

	Constructed->BindCargoHull();
	TestNotNull(
		TEXT("BindCargoHull without authored mesh does not crash and binds a hull"),
		Constructed->GetHull()->GetStaticMesh());
	if (Constructed->GetHull()->GetStaticMesh())
	{
		TestEqual(
			TEXT("ProxyFallback engine Cube is used when no authored cargo mesh exists"),
			Constructed->GetHull()->GetStaticMesh()->GetName(),
			FString(TEXT("Cube")));
	}

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardProtectAssetBindWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}
	ASkyguardProtectAsset* Spawned =
		World->SpawnActor<ASkyguardProtectAsset>();
	TestNotNull(TEXT("spawned ProtectAsset"), Spawned);
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
		TEXT("BeginPlay binds cargo hull without authored mesh"),
		Spawned->GetHull()->GetStaticMesh());
	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardProtectAssetPreferredSlotsStayEmptyTest,
	"Skyguard52.MeshBind.ProtectAsset.PreferredSlotsStayEmpty",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardProtectAssetPreferredSlotsStayEmptyTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardProtectAssetTests;

	const FSkyguardMeshBindSlot CargoSlot =
		ASkyguardProtectAsset::MakeCargoHullBindSlot();
	TestEqual(
		TEXT("cargo hull slot id"),
		CargoSlot.SlotId,
		FName(TEXT("ProtectAsset.CargoHull")));
	TestTrue(
		TEXT("cargo hull Preferred stays empty"),
		CargoSlot.Preferred.IsNull());
	TestFalse(
		TEXT("cargo hull ProxyFallback is set"),
		CargoSlot.ProxyFallback.IsNull());
	TestTrue(
		TEXT("cargo hull ProxyFallback is the engine Cube primitive"),
		CargoSlot.ProxyFallback.ToSoftObjectPath().ToString().Contains(
			TEXT("/Engine/BasicShapes/Cube")));
	TestFalse(
		TEXT("cargo hull ProxyFallback is not a Harbor kit path"),
		PathLooksLikeHarborKit(CargoSlot.ProxyFallback.ToSoftObjectPath()));

	bool bSawTruckSlot = false;
	for (const FSkyguardMeshBindSlot& Slot :
		USkyguardRuntimeMeshCatalog::GetCodeDefaultSlots())
	{
		if (SlotIdLooksLikeHarborKitFill(Slot.SlotId))
		{
			TestTrue(
				*FString::Printf(
					TEXT("Harbor kit ship/boat/truck slot '%s' Preferred stays empty"),
					*Slot.SlotId.ToString()),
				Slot.Preferred.IsNull());
			TestFalse(
				*FString::Printf(
					TEXT("Harbor kit slot '%s' Preferred is not a Harbor kit fill"),
					*Slot.SlotId.ToString()),
				PathLooksLikeHarborKit(Slot.Preferred.ToSoftObjectPath()));
		}
		if (Slot.SlotId == TEXT("Vehicle.Truck"))
		{
			bSawTruckSlot = true;
			TestTrue(
				TEXT("Vehicle.Truck Preferred stays empty"),
				Slot.Preferred.IsNull());
		}
		TestFalse(
			*FString::Printf(
				TEXT("catalog slot '%s' Preferred is not a Harbor kit fill"),
				*Slot.SlotId.ToString()),
			PathLooksLikeHarborKit(Slot.Preferred.ToSoftObjectPath()));
	}
	TestTrue(TEXT("Vehicle.Truck remains a catalog slot"), bSawTruckSlot);
	return true;
}

#endif
