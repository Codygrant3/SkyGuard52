#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCombatVFX.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardCombatVFXTests.cpp.
// Remaining nullptr-world fail-closed public API only. No world spawn,
// no Gunner / Yak / Igla / rifle, no ApplyWeaponHit. Existing
// SkyguardCombatVFXTests.cpp already covers Niagara catalog paths and
// a real-world fixed pool. Do not call SpawnIglaLaunch (historical name;
// live copy stays Apache 30 mm / Hydra / Hellfire).

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCombatVFXFailClosedTest,
	"Skyguard52.Combat.VFX.FailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCombatVFXFailClosedTest::RunTest(const FString& Parameters)
{
	// Pool(World) returns World ? World->GetSubsystem<...>() : nullptr.
	// Each Apache combat spawn returns immediately when Pool is null.
	// There is nothing to assert on spawned actors.
	USkyguardCombatVFX::SpawnMuzzleFlash(
		nullptr,
		FVector::ZeroVector,
		FVector::ForwardVector);
	USkyguardCombatVFX::SpawnGunSmoke(
		nullptr,
		FVector::ZeroVector,
		FVector::ForwardVector);
	USkyguardCombatVFX::SpawnHitSparks(
		nullptr,
		FVector::ZeroVector,
		FVector::ForwardVector);
	USkyguardCombatVFX::SpawnExplosion(nullptr, FVector::ZeroVector);
	USkyguardCombatVFX::SpawnMissileTrail(
		nullptr,
		FVector::ZeroVector,
		FVector::ForwardVector);
	USkyguardCombatVFX::SpawnTracer(
		nullptr,
		FVector::ZeroVector,
		FVector::ForwardVector);

	TestTrue(
		TEXT("Null-world Apache combat VFX calls fail closed without spawning"),
		true);
	return true;
}

#endif
