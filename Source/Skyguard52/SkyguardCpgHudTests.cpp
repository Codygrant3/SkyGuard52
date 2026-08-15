#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgHud.h"
#include "SkyguardDrone.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardThreatTypes.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgHudTapesWeaponRangeThreatTest,
	"Skyguard52.Apache.CpgHudTapesWeaponRangeThreat",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgHudTapesWeaponRangeThreatTest::RunTest(const FString& Parameters)
{
	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	FSkyguardCpgHudSnapshot Cannon = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("cannon tape names 30 mm"), Cannon.WeaponLine.Contains(TEXT("30MM")));
	TestTrue(TEXT("cannon tape shows ready"), Cannon.WeaponLine.Contains(TEXT("RDY")));
	TestTrue(TEXT("empty world is clear"), Cannon.ThreatLine.Contains(TEXT("CLR")));
	TestTrue(TEXT("no range without a camera hit"), Cannon.RangeLine.Contains(TEXT("----")));
	TestEqual(TEXT("no contacts"), Cannon.ThreatCount, 0);
	TestFalse(
		TEXT("cannon tape is not a Yak/Igla/rifle label"),
		SkyguardCpgHudHasLegacyLiveWording(Cannon.WeaponLine));

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	FSkyguardCpgHudSnapshot Rockets = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("rocket tape names rockets"), Rockets.WeaponLine.Contains(TEXT("RKT")));
	TestFalse(
		TEXT("rocket tape is not a Yak/Igla/rifle label"),
		SkyguardCpgHudHasLegacyLiveWording(Rockets.WeaponLine));

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	FSkyguardCpgHudSnapshot Missile = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("missile tape names guided missiles"), Missile.WeaponLine.Contains(TEXT("MSL")));
	TestTrue(TEXT("missile tape shows search before lock"), Missile.WeaponLine.Contains(TEXT("SRCH")));
	TestTrue(TEXT("eufd carries the station"), Missile.EufdLine.Contains(TEXT("MSL")));
	TestTrue(TEXT("eufd carries lock state"), Missile.EufdLine.Contains(TEXT("SRCH")));
	TestTrue(TEXT("eufd names helmet-sight"), Missile.EufdLine.Contains(TEXT("HMD")));
	TestEqual(
		TEXT("open seeker is search"),
		Missile.LockPhase,
		ESkyguardGuidedLockPhase::Search);
	TestEqual(
		TEXT("default sight is helmet"),
		Missile.SightMode,
		ESkyguardCpgSightMode::Helmet);
	TestFalse(
		TEXT("missile tape is not a Yak/Igla/rifle label"),
		SkyguardCpgHudHasLegacyLiveWording(Missile.WeaponLine + Missile.EufdLine + Missile.LockLine));

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Cannon);
	Gunner->ReloadSelectedWeapon();
	FSkyguardCpgHudSnapshot Reload = Gunner->BuildCpgHudSnapshot();
	TestTrue(
		TEXT("full magazine does not start a reload"),
		Reload.WeaponLine.Contains(TEXT("RDY")));

	TestEqual(
		TEXT("weapon label helper"),
		FString(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::Rockets)),
		FString(TEXT("RKT")));
	TestEqual(
		TEXT("cannon label helper"),
		FString(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::Cannon)),
		FString(TEXT("30MM")));
	TestEqual(
		TEXT("missile label helper"),
		FString(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::GuidedMissile)),
		FString(TEXT("MSL")));
	TestTrue(
		TEXT("legacy Igla wording is rejected"),
		SkyguardCpgHudHasLegacyLiveWording(FString(TEXT("Igla"))));
	TestTrue(
		TEXT("legacy Yak wording is rejected"),
		SkyguardCpgHudHasLegacyLiveWording(FString(TEXT("Yak-52"))));
	TestTrue(
		TEXT("legacy rifle wording is rejected"),
		SkyguardCpgHudHasLegacyLiveWording(FString(TEXT("rear rifle"))));
	TestFalse(
		TEXT("live station labels are clean"),
		SkyguardCpgHudHasLegacyLiveWording(FString(TEXT("30MM RKT MSL LCK"))));
	TestEqual(
		TEXT("threat label helper"),
		FString(SkyguardCpgThreatLabel(ESkyguardThreatKind::GroundArmor)),
		FString(TEXT("ARM")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgHudCountsForwardThreatTest,
	"Skyguard52.Apache.CpgHudCountsForwardThreat",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgHudCountsForwardThreatTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardCpgHudThreatWorld"));
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
	const FSkyguardCpgHudSnapshot Snap = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("forward armor is a contact"), Snap.ThreatCount >= 1);
	TestTrue(TEXT("threat tape names armor"), Snap.ThreatLine.Contains(TEXT("ARM")));

	TArray<FSkyguardCpgContactMark> Marks;
	Gunner->CollectCpgContactMarks(Marks);
	TestTrue(TEXT("contact marks include the forward armor"), Marks.Num() >= 1);
	bool bFoundArmor = false;
	for (const FSkyguardCpgContactMark& Mark : Marks)
	{
		if (Mark.Label == TEXT("ARM"))
		{
			bFoundArmor = true;
			TestFalse(TEXT("unacquired contact is not locked"), Mark.bLocked);
		}
	}
	TestTrue(TEXT("armor mark is labeled ARM"), bFoundArmor);

	World->DestroyWorld(false);
	return true;
}

#endif
