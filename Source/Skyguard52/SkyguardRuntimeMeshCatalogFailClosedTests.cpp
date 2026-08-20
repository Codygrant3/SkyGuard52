#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardRuntimeMeshCatalog.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardRuntimeMeshCatalogTests.cpp.
// Remaining unknown-slot / empty-catalog fail-closed public API only.
// NewObject, no EnsureDefaultSlots, no Gunner / Yak / Igla / rifle spawn.
// Existing SkyguardRuntimeMeshCatalogTests.cpp already covers Cube-over-Sphere
// Preferred wins, ProxyFallback, and briefing-widget smoke.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRuntimeMeshCatalogFailClosedTest,
	"Skyguard52.MeshBind.Catalog.FailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRuntimeMeshCatalogFailClosedTest::RunTest(const FString& Parameters)
{
	USkyguardRuntimeMeshCatalog* Catalog =
		NewObject<USkyguardRuntimeMeshCatalog>();
	TestNotNull(TEXT("NewObject catalog constructs"), Catalog);
	if (!Catalog)
	{
		return false;
	}

	const FName MissingSlotId(TEXT("DoesNotExist"));

	TestNull(
		TEXT("FindSlot(NAME_None) is nullptr on an empty catalog"),
		Catalog->FindSlot(NAME_None));
	TestNull(
		TEXT("FindSlot(DoesNotExist) is nullptr when no SlotId matches"),
		Catalog->FindSlot(MissingSlotId));

	TestNull(
		TEXT("ResolveMesh(NAME_None) is nullptr when FindSlot misses and no default matches"),
		Catalog->ResolveMesh(NAME_None));
	TestNull(
		TEXT("ResolveMesh(DoesNotExist) is nullptr when FindSlot misses and no default matches"),
		Catalog->ResolveMesh(MissingSlotId));

	TestNull(
		TEXT("ResolveDefaultSlot(NAME_None) is nullptr when no code-default SlotId matches"),
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(NAME_None));
	TestNull(
		TEXT("ResolveDefaultSlot(DoesNotExist) is nullptr when no code-default SlotId matches"),
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(MissingSlotId));

	const FSkyguardMeshBindSlot EmptySlot;
	TestTrue(
		TEXT("Default FSkyguardMeshBindSlot Preferred is empty"),
		EmptySlot.Preferred.IsNull());
	TestTrue(
		TEXT("Default FSkyguardMeshBindSlot ProxyFallback is empty"),
		EmptySlot.ProxyFallback.IsNull());
	TestNull(
		TEXT("ResolveSlot of empty Preferred and ProxyFallback returns nullptr without a mesh load"),
		USkyguardRuntimeMeshCatalog::ResolveSlot(EmptySlot));

	return true;
}

#endif
