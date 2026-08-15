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
	TestTrue(TEXT("cannon tape names M230"), Cannon.WeaponLine.Contains(TEXT("M230")));
	TestTrue(TEXT("cannon tape shows ready"), Cannon.WeaponLine.Contains(TEXT("RDY")));
	TestTrue(TEXT("empty world is clear"), Cannon.ThreatLine.Contains(TEXT("CLR")));
	TestTrue(TEXT("no range without a camera hit"), Cannon.RangeLine.Contains(TEXT("----")));
	TestEqual(TEXT("no contacts"), Cannon.ThreatCount, 0);

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	FSkyguardCpgHudSnapshot Rockets = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("rocket tape names HYDRA"), Rockets.WeaponLine.Contains(TEXT("HYDRA")));

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	FSkyguardCpgHudSnapshot Missile = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("missile tape names HLF"), Missile.WeaponLine.Contains(TEXT("HLF")));
	TestTrue(TEXT("eufd carries the station"), Missile.EufdLine.Contains(TEXT("HLF")));

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Cannon);
	Gunner->ReloadSelectedWeapon();
	FSkyguardCpgHudSnapshot Reload = Gunner->BuildCpgHudSnapshot();
	TestTrue(
		TEXT("full magazine does not start a reload"),
		Reload.WeaponLine.Contains(TEXT("RDY")));

	TestEqual(
		TEXT("weapon label helper"),
		FString(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::Rockets)),
		FString(TEXT("HYDRA")));
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
