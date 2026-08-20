#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCombatNiagaraCatalog.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardCombatVFXTests.cpp.
// Locks the exact Apache CPG Niagara soft-path strings from origin/main.
// Static FSoftObjectPath getters only. No world, no Niagara spawn,
// no Gunner / Yak / Igla / rifle. Existing SkyguardCombatVFXTests.cpp
// already checks that six catalog paths (including GetIglaLaunchPath)
// are non-empty. Do not call GetIglaLaunchPath here (historical path
// exists; Igla is not a live Apache CPG player weapon). Do not call
// ResolveMuzzleFlash / ResolveGunSmoke / ResolveHitSparks /
// ResolveDroneExplosion / ResolveMissileTrail / ResolveIglaLaunch
// (those TryLoad packages).

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCombatNiagaraCatalogCpgPathTest,
	"Skyguard52.Combat.VFX.NiagaraCatalog.ApacheCpgSoftPaths",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCombatNiagaraCatalogCpgPathTest::RunTest(
	const FString& Parameters)
{
	TestEqual(
		TEXT("GetMuzzleFlashPath is the Apache CPG Niagara soft path"),
		USkyguardCombatNiagaraCatalog::GetMuzzleFlashPath().ToString(),
		FString(TEXT("/Game/Skyguard/VFX/NS_MuzzleFlash.NS_MuzzleFlash")));
	TestEqual(
		TEXT("GetGunSmokePath is the Apache CPG Niagara soft path"),
		USkyguardCombatNiagaraCatalog::GetGunSmokePath().ToString(),
		FString(TEXT("/Game/Skyguard/VFX/NS_GunSmoke.NS_GunSmoke")));
	TestEqual(
		TEXT("GetHitSparksPath is the Apache CPG Niagara soft path"),
		USkyguardCombatNiagaraCatalog::GetHitSparksPath().ToString(),
		FString(TEXT("/Game/Skyguard/VFX/NS_HitSparks.NS_HitSparks")));
	TestEqual(
		TEXT("GetDroneExplosionPath is the Apache CPG Niagara soft path"),
		USkyguardCombatNiagaraCatalog::GetDroneExplosionPath().ToString(),
		FString(TEXT("/Game/Skyguard/VFX/NS_DroneExplosion.NS_DroneExplosion")));
	TestEqual(
		TEXT("GetMissileTrailPath is the Apache CPG Niagara soft path"),
		USkyguardCombatNiagaraCatalog::GetMissileTrailPath().ToString(),
		FString(TEXT("/Game/Skyguard/VFX/NS_MissileTrail.NS_MissileTrail")));
	return true;
}

#endif
