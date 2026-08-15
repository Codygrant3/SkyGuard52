#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardDrone.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardThreatTypes.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheStationsAreCannonRocketsMissileTest,
	"Skyguard52.Apache.StationsAreCannonRocketsMissile",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheStationsAreCannonRocketsMissileTest::RunTest(
	const FString& Parameters)
{
	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}
	TestEqual(
		TEXT("default station is cannon"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::Cannon);
	TestTrue(TEXT("rocket magazine is loaded"), Gunner->GetRocketAmmo() > 0);
	TestTrue(TEXT("guided magazine is loaded"), Gunner->GetGuidedAmmo() > 0);
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	TestEqual(
		TEXT("2 selects rockets"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::Rockets);
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	TestEqual(
		TEXT("3 selects guided missiles"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::GuidedMissile);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheReloadFillsMagazineTest,
	"Skyguard52.Apache.ReloadFillsMagazine",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheReloadFillsMagazineTest::RunTest(const FString& Parameters)
{
	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Cannon);
	Gunner->CannonMagazine = 0;
	Gunner->CannonReserve = 30;
	TestFalse(TEXT("not reloading at rest"), Gunner->IsReloading());
	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("R starts a reload"), Gunner->IsReloading());
	Gunner->AdvanceReload(2.f);
	TestFalse(TEXT("reload finishes"), Gunner->IsReloading());
	TestEqual(TEXT("magazine is filled from reserve"), Gunner->GetCannonMagazine(), 30);
	TestEqual(TEXT("reserve is consumed"), Gunner->CannonReserve, 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardThreatRosterHasNonDroneKindsTest,
	"Skyguard52.Threats.RosterHasLandSeaAir",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardThreatRosterHasNonDroneKindsTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardThreatRosterWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardDrone* Armor = World->SpawnActor<ASkyguardDrone>();
	ASkyguardDrone* Boat = World->SpawnActor<ASkyguardDrone>();
	ASkyguardDrone* Scout = World->SpawnActor<ASkyguardDrone>();
	ASkyguardDrone* Fast = World->SpawnActor<ASkyguardDrone>();
	TestNotNull(TEXT("armor"), Armor);
	TestNotNull(TEXT("boat"), Boat);
	TestNotNull(TEXT("scout"), Scout);
	TestNotNull(TEXT("fast"), Fast);
	if (!Armor || !Boat || !Scout || !Fast)
	{
		World->DestroyWorld(false);
		return false;
	}

	Armor->ConfigureThreat(ESkyguardThreatKind::GroundArmor);
	Boat->ConfigureThreat(ESkyguardThreatKind::FastBoat);
	Scout->ConfigureThreat(ESkyguardThreatKind::RotorScout);
	Fast->ConfigureThreat(ESkyguardThreatKind::FastAttacker);

	TestTrue(TEXT("armor is missile eligible"), Armor->IsMissileLockEligible());
	TestTrue(TEXT("boat is missile eligible"), Boat->IsMissileLockEligible());
	TestTrue(TEXT("scout is missile eligible"), Scout->IsMissileLockEligible());
	TestFalse(TEXT("fast attacker is cannon food"), Fast->IsMissileLockEligible());
	TestTrue(TEXT("armor is tougher than a scout"), Armor->MaxHealth > Scout->MaxHealth);

	World->DestroyWorld(false);
	return true;
}

#endif
