#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGunner.h"
#include "SkyguardGunshipTypes.h"

#include "Misc/AutomationTest.h"
#include "UObject/UnrealType.h"

namespace SkyguardApacheCannonReloadTests
{
	bool WriteIntField(UObject* Object, const FName Name, const int32 Value)
	{
		if (!Object)
		{
			return false;
		}
		const FIntProperty* Property =
			FindFProperty<FIntProperty>(Object->GetClass(), Name);
		if (!Property)
		{
			return false;
		}
		Property->SetPropertyValue_InContainer(Object, Value);
		return true;
	}

	bool ReadIntField(const UObject* Object, const FName Name, int32& OutValue)
	{
		if (!Object)
		{
			return false;
		}
		const FIntProperty* Property =
			FindFProperty<FIntProperty>(Object->GetClass(), Name);
		if (!Property)
		{
			return false;
		}
		OutValue = Property->GetPropertyValue_InContainer(Object);
		return true;
	}

	const TCHAR* ReadyFieldName(const ESkyguardGunshipWeapon Station)
	{
		switch (Station)
		{
		case ESkyguardGunshipWeapon::Rockets:
			return TEXT("RocketAmmo");
		case ESkyguardGunshipWeapon::GuidedMissile:
			return TEXT("GuidedAmmo");
		case ESkyguardGunshipWeapon::Cannon:
			return TEXT("CannonMagazine");
		}
		checkNoEntry();
		return TEXT("CannonMagazine");
	}

	const TCHAR* ReserveFieldName(const ESkyguardGunshipWeapon Station)
	{
		switch (Station)
		{
		case ESkyguardGunshipWeapon::Rockets:
			return TEXT("RocketReserve");
		case ESkyguardGunshipWeapon::GuidedMissile:
			return TEXT("GuidedReserve");
		case ESkyguardGunshipWeapon::Cannon:
			return TEXT("CannonReserve");
		}
		checkNoEntry();
		return TEXT("CannonReserve");
	}

	bool SetReadyAmmo(
		ASkyguardGunner& Gunner,
		const ESkyguardGunshipWeapon Station,
		const int32 Ready)
	{
		return WriteIntField(&Gunner, ReadyFieldName(Station), Ready);
	}

	bool SetReserve(
		ASkyguardGunner& Gunner,
		const ESkyguardGunshipWeapon Station,
		const int32 Reserve)
	{
		return WriteIntField(&Gunner, ReserveFieldName(Station), Reserve);
	}

	bool GetReserve(
		const ASkyguardGunner& Gunner,
		const ESkyguardGunshipWeapon Station,
		int32& OutReserve)
	{
		return ReadIntField(&Gunner, ReserveFieldName(Station), OutReserve);
	}

	void CompletePublicReload(ASkyguardGunner& Gunner)
	{
		Gunner.Tick(SkyguardApacheCpgFeel::CannonReloadSeconds + 0.1f);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheCannonReloadsToMagazineTest,
	"Skyguard52.Apache.CannonReloadsToMagazine",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheCannonReloadsToMagazineTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardApacheCannonReloadTests;

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	Gunner->ApplyLoadout(ESkyguardLoadout::Balanced);
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Cannon);
	TestEqual(
		TEXT("balanced 30mm magazine is the CPG feel size"),
		Gunner->GetCannonMagazine(),
		SkyguardApacheCpgFeel::CannonMagazineSize);
	TestTrue(
		TEXT("wrote an empty 30mm magazine"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Cannon, 0));
	TestEqual(TEXT("30mm magazine starts empty"), Gunner->GetCannonMagazine(), 0);
	TestFalse(TEXT("not reloading at rest"), Gunner->IsReloading());

	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("R starts a 30mm reload"), Gunner->IsReloading());
	CompletePublicReload(*Gunner);
	TestFalse(TEXT("30mm reload finishes"), Gunner->IsReloading());
	TestEqual(
		TEXT("empty 30mm magazine refills to the designed loadout magazine"),
		Gunner->GetCannonMagazine(),
		SkyguardApacheCpgFeel::CannonMagazineSize);

	TestTrue(
		TEXT("wrote a partial 30mm magazine"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Cannon, 8));
	TestEqual(TEXT("30mm magazine is partial"), Gunner->GetCannonMagazine(), 8);
	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("R starts a partial 30mm reload"), Gunner->IsReloading());
	CompletePublicReload(*Gunner);
	TestFalse(TEXT("partial 30mm reload finishes"), Gunner->IsReloading());
	TestEqual(
		TEXT("partial 30mm magazine refills to the designed loadout magazine"),
		Gunner->GetCannonMagazine(),
		SkyguardApacheCpgFeel::CannonMagazineSize);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheCannonReloadLeavesHydraAndHellfireAloneTest,
	"Skyguard52.Apache.CannonReloadLeavesHydraAndHellfireAlone",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheCannonReloadLeavesHydraAndHellfireAloneTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardApacheCannonReloadTests;

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	Gunner->ApplyLoadout(ESkyguardLoadout::Balanced);
	TestTrue(
		TEXT("wrote empty 30mm magazine"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Cannon, 0));
	TestTrue(
		TEXT("wrote leftover Hydra pods"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Rockets, 4));
	TestTrue(
		TEXT("wrote leftover Hellfire rails"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::GuidedMissile, 1));
	const int32 HydraBefore = Gunner->GetRocketAmmo();
	const int32 HellfireBefore = Gunner->GetGuidedAmmo();
	TestEqual(TEXT("Hydra leftover is in place"), HydraBefore, 4);
	TestEqual(TEXT("Hellfire leftover is in place"), HellfireBefore, 1);
	TestTrue(
		TEXT("Hydra leftover is not the balanced default"),
		HydraBefore != SkyguardApacheCpgFeel::RocketMagazineSize);
	TestTrue(
		TEXT("Hellfire leftover is not the balanced default"),
		HellfireBefore != SkyguardApacheCpgFeel::GuidedMagazineSize);

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Cannon);
	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("R starts a 30mm reload"), Gunner->IsReloading());
	CompletePublicReload(*Gunner);
	TestFalse(TEXT("30mm reload finishes"), Gunner->IsReloading());
	TestEqual(
		TEXT("30mm refill uses the designed cannon magazine"),
		Gunner->GetCannonMagazine(),
		SkyguardApacheCpgFeel::CannonMagazineSize);
	TestEqual(
		TEXT("cannon reload leaves Hydra ready count alone"),
		Gunner->GetRocketAmmo(),
		HydraBefore);
	TestEqual(
		TEXT("cannon reload leaves Hellfire ready count alone"),
		Gunner->GetGuidedAmmo(),
		HellfireBefore);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheCannonReloadDoesNotInventPastCapTest,
	"Skyguard52.Apache.CannonReloadDoesNotInventPastCap",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheCannonReloadDoesNotInventPastCapTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardApacheCannonReloadTests;

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	Gunner->ApplyLoadout(ESkyguardLoadout::Balanced);
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Cannon);
	TestEqual(
		TEXT("full 30mm magazine sits at the designed cap"),
		Gunner->GetCannonMagazine(),
		SkyguardApacheCpgFeel::CannonMagazineSize);
	Gunner->ReloadSelectedWeapon();
	TestFalse(
		TEXT("full 30mm magazine does not start a reload"),
		Gunner->IsReloading());
	TestEqual(
		TEXT("full 30mm reload does not invent past the cap"),
		Gunner->GetCannonMagazine(),
		SkyguardApacheCpgFeel::CannonMagazineSize);

	TestTrue(
		TEXT("wrote empty 30mm magazine"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Cannon, 0));
	TestTrue(
		TEXT("wrote a short 30mm reserve"),
		SetReserve(*Gunner, ESkyguardGunshipWeapon::Cannon, 7));
	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("short 30mm reserve still starts a reload"), Gunner->IsReloading());
	CompletePublicReload(*Gunner);
	TestEqual(
		TEXT("30mm reload takes only the remaining reserve"),
		Gunner->GetCannonMagazine(),
		7);
	TestTrue(
		TEXT("short 30mm reserve does not invent a full magazine"),
		Gunner->GetCannonMagazine() < SkyguardApacheCpgFeel::CannonMagazineSize);
	int32 CannonReserve = -1;
	TestTrue(
		TEXT("read 30mm reserve"),
		GetReserve(*Gunner, ESkyguardGunshipWeapon::Cannon, CannonReserve));
	TestEqual(TEXT("30mm reserve is spent"), CannonReserve, 0);

	TestTrue(
		TEXT("wrote empty 30mm magazine with no reserve"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Cannon, 0));
	TestTrue(
		TEXT("wrote a zero 30mm reserve"),
		SetReserve(*Gunner, ESkyguardGunshipWeapon::Cannon, 0));
	Gunner->ReloadSelectedWeapon();
	TestFalse(
		TEXT("empty 30mm magazine with no reserve does not invent a reload"),
		Gunner->IsReloading());
	TestEqual(TEXT("empty 30mm magazine stays empty"), Gunner->GetCannonMagazine(), 0);

	const FSkyguardLoadoutSpec AntiArmor =
		SkyguardResolveLoadout(ESkyguardLoadout::AntiArmor);
	TestTrue(
		TEXT("anti-armor 30mm magazine is smaller than the default CPG feel"),
		AntiArmor.CannonMagazineSize < SkyguardApacheCpgFeel::CannonMagazineSize);
	Gunner->ApplyLoadout(ESkyguardLoadout::AntiArmor);
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Cannon);
	TestEqual(
		TEXT("anti-armor loadout applies its cannon magazine"),
		Gunner->GetCannonMagazine(),
		AntiArmor.CannonMagazineSize);
	TestTrue(
		TEXT("wrote empty anti-armor 30mm magazine"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Cannon, 0));

	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("R starts an anti-armor 30mm reload"), Gunner->IsReloading());
	CompletePublicReload(*Gunner);
	TestEqual(
		TEXT("anti-armor 30mm reload stops at that loadout cannon magazine"),
		Gunner->GetCannonMagazine(),
		AntiArmor.CannonMagazineSize);
	TestTrue(
		TEXT("anti-armor 30mm reload does not invent the default CPG feel cap"),
		Gunner->GetCannonMagazine() != SkyguardApacheCpgFeel::CannonMagazineSize);
	return true;
}

#endif
