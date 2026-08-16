#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgHud.h"
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
	TestEqual(
		TEXT("1 / station label is M230 not Igla"),
		FString(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::Cannon)),
		FString(TEXT("M230")));
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	TestEqual(
		TEXT("2 selects rockets"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::Rockets);
	TestEqual(
		TEXT("2 / station label is HYDRA"),
		FString(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::Rockets)),
		FString(TEXT("HYDRA")));
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	TestEqual(
		TEXT("3 selects guided missiles"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::GuidedMissile);
	TestEqual(
		TEXT("3 / station label is HLF not Igla"),
		FString(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::GuidedMissile)),
		FString(TEXT("HLF")));
	TestFalse(
		TEXT("guided label does not say Igla"),
		FString(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::GuidedMissile))
			.Contains(TEXT("Igla")));
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
	FSkyguardApacheCannonEmptyMagazineRefusesFireTest,
	"Skyguard52.Apache.CannonEmptyMagazineRefusesFire",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheCannonEmptyMagazineRefusesFireTest::RunTest(
	const FString& Parameters)
{
	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	Gunner->bApacheGunnerMode = true;
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Cannon);
	Gunner->CannonMagazine = 0;
	Gunner->CannonReserve = SkyguardApacheCpgFeel::CannonMagazineSize;
	const int32 ShotsBefore = Gunner->GetSortieShotsFired();
	Gunner->FireCannon();
	TestEqual(TEXT("empty mag stays empty"), Gunner->GetCannonMagazine(), 0);
	TestEqual(TEXT("empty mag does not spend a shot"), Gunner->GetSortieShotsFired(), ShotsBefore);

	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("R starts a reload"), Gunner->IsReloading());
	Gunner->AdvanceReload(SkyguardApacheCpgFeel::CannonReloadSeconds + 0.1f);
	TestFalse(TEXT("reload finishes"), Gunner->IsReloading());
	TestEqual(
		TEXT("reload fills from reserve"),
		Gunner->GetCannonMagazine(),
		SkyguardApacheCpgFeel::CannonMagazineSize);
	TestEqual(TEXT("reserve is consumed"), Gunner->CannonReserve, 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheRocketSalvoConsumesAndCoolsTest,
	"Skyguard52.Apache.RocketSalvoConsumesAndCools",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheRocketSalvoConsumesAndCoolsTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheRocketSalvoWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>(
		FVector::ZeroVector,
		FRotator::ZeroRotator);
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		World->DestroyWorld(false);
		return false;
	}

	Gunner->bApacheGunnerMode = true;
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	Gunner->RocketAmmo = SkyguardApacheCpgFeel::RocketMagazineSize;
	Gunner->RocketCooldown = 0.f;
	Gunner->FireCooldown = 0.f;
	Gunner->FireRockets();

	const int32 ExpectedRemaining =
		SkyguardApacheCpgFeel::RocketMagazineSize - SkyguardApacheCpgFeel::RocketsPerSalvo;
	TestEqual(
		TEXT("salvo spends RocketsPerSalvo"),
		Gunner->GetRocketAmmo(),
		ExpectedRemaining);
	TestTrue(
		TEXT("salvo cooldown is at least one cannon interval"),
		Gunner->RocketCooldown >= 1.f / SkyguardApacheCpgFeel::CannonFireRate);
	TestTrue(
		TEXT("salvo wait is longer than a cannon shot"),
		Gunner->RocketCooldown >= SkyguardApacheCpgFeel::RocketSalvoSeconds - KINDA_SMALL_NUMBER);
	TestTrue(
		TEXT("hold-fire cooldown keeps the salvo wait"),
		Gunner->FireCooldown >= SkyguardApacheCpgFeel::RocketSalvoSeconds - KINDA_SMALL_NUMBER);
	TestTrue(
		TEXT("spread is wide enough that rockets are not a sniper"),
		Gunner->RocketSpreadDegrees >= 5.f);

	Gunner->RocketAmmo = 2;
	Gunner->RocketCooldown = 0.f;
	Gunner->FireCooldown = 0.f;
	Gunner->FireRockets();
	TestEqual(TEXT("short magazine spends the remaining rockets"), Gunner->GetRocketAmmo(), 0);
	TestTrue(
		TEXT("partial salvo still commits a wait"),
		Gunner->RocketCooldown >= 1.f / SkyguardApacheCpgFeel::CannonFireRate);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheMissileRequiresLockAndAmmoTest,
	"Skyguard52.Apache.MissileRequiresLockAndAmmo",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheMissileRequiresLockAndAmmoTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheMissileGateWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>(
		FVector::ZeroVector,
		FRotator::ZeroRotator);
	ASkyguardDrone* Armor = World->SpawnActor<ASkyguardDrone>(
		FVector(2000.f, 0.f, 0.f),
		FRotator::ZeroRotator);
	TestNotNull(TEXT("gunner"), Gunner);
	TestNotNull(TEXT("armor"), Armor);
	if (!Gunner || !Armor)
	{
		World->DestroyWorld(false);
		return false;
	}

	Armor->ConfigureThreat(ESkyguardThreatKind::GroundArmor);
	Gunner->bApacheGunnerMode = true;
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	Gunner->GuidedAmmo = SkyguardApacheCpgFeel::GuidedMagazineSize;
	Gunner->IglaTarget = Armor;
	Gunner->IglaLockProgress = 0.4f;
	const int32 AmmoBefore = Gunner->GetGuidedAmmo();
	Gunner->FireGuidedMissile();
	TestEqual(
		TEXT("no fire without a completed lock"),
		Gunner->GetGuidedAmmo(),
		AmmoBefore);
	TestEqual(
		TEXT("partial lock is left in place"),
		Gunner->IglaLockProgress,
		0.4f);

	Gunner->IglaTarget.Reset();
	Gunner->IglaLockProgress = 1.f;
	Gunner->FireGuidedMissile();
	TestEqual(
		TEXT("no fire without a lock target"),
		Gunner->GetGuidedAmmo(),
		AmmoBefore);

	Gunner->IglaTarget = Armor;
	Gunner->IglaLockProgress = 1.f;
	Gunner->GuidedAmmo = 0;
	Gunner->FireGuidedMissile();
	TestEqual(TEXT("no fire without guided ammo"), Gunner->GetGuidedAmmo(), 0);
	TestTrue(TEXT("empty tube keeps the lock"), Gunner->IglaLockProgress >= 1.f);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheMissileLockEligibilityTest,
	"Skyguard52.Apache.MissileLockEligibility",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheMissileLockEligibilityTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheLockEligibilityWorld"));
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

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheCannonWorseValueThanMissileTest,
	"Skyguard52.Apache.CannonWorseValueThanMissile",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheCannonWorseValueThanMissileTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheWeaponValueWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	ASkyguardDrone* Armor = World->SpawnActor<ASkyguardDrone>();
	TestNotNull(TEXT("gunner"), Gunner);
	TestNotNull(TEXT("armor"), Armor);
	if (!Gunner || !Armor)
	{
		World->DestroyWorld(false);
		return false;
	}

	Armor->ConfigureThreat(ESkyguardThreatKind::GroundArmor);
	TestEqual(
		TEXT("cannon damage is the CPG feel number"),
		Gunner->BaseDamage,
		SkyguardApacheCpgFeel::CannonDamage);
	TestEqual(
		TEXT("missile damage is the CPG feel number"),
		Gunner->IglaDamage,
		SkyguardApacheCpgFeel::GuidedDamage);
	TestEqual(
		TEXT("cannon rate is the CPG feel number"),
		Gunner->FireRate,
		SkyguardApacheCpgFeel::CannonFireRate);
	TestTrue(
		TEXT("armor takes a cannon burst, not a tap"),
		Armor->MaxHealth > Gunner->BaseDamage * 5.f);
	TestTrue(
		TEXT("one missile answers armor"),
		Gunner->IglaDamage >= Armor->MaxHealth);
	TestTrue(
		TEXT("one missile is better value than eight cannon hits"),
		Gunner->IglaDamage > Gunner->BaseDamage * 8.f);
	TestTrue(
		TEXT("lock is a hold, not instant"),
		Gunner->IglaLockSeconds >= 1.5f);
	TestTrue(
		TEXT("rocket salvo is slower than a cannon shot"),
		Gunner->RocketSalvoSeconds > 1.f / Gunner->FireRate);

	World->DestroyWorld(false);
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
