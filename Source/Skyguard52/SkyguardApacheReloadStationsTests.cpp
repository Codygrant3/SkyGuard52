#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGunner.h"
#include "SkyguardGunshipTypes.h"

#include "Misc/AutomationTest.h"
#include "UObject/UnrealType.h"

namespace SkyguardApacheReloadStationsTests
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

	float ReloadSeconds(const ESkyguardGunshipWeapon Station)
	{
		switch (Station)
		{
		case ESkyguardGunshipWeapon::Rockets:
			return SkyguardApacheCpgFeel::RocketReloadSeconds;
		case ESkyguardGunshipWeapon::GuidedMissile:
			return SkyguardApacheCpgFeel::GuidedReloadSeconds;
		case ESkyguardGunshipWeapon::Cannon:
			return SkyguardApacheCpgFeel::CannonReloadSeconds;
		}
		checkNoEntry();
		return SkyguardApacheCpgFeel::CannonReloadSeconds;
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

	void CompletePublicReload(ASkyguardGunner& Gunner, const ESkyguardGunshipWeapon Station)
	{
		Gunner.Tick(ReloadSeconds(Station) + 0.1f);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheHydraPodsReloadToMagazineTest,
	"Skyguard52.Apache.HydraPodsReloadToMagazine",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheHydraPodsReloadToMagazineTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardApacheReloadStationsTests;

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	Gunner->ApplyLoadout(ESkyguardLoadout::Balanced);
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	TestEqual(
		TEXT("balanced Hydra magazine is the CPG feel size"),
		Gunner->GetRocketAmmo(),
		SkyguardApacheCpgFeel::RocketMagazineSize);
	TestTrue(
		TEXT("wrote empty Hydra pods"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Rockets, 0));
	TestEqual(TEXT("Hydra pods start empty"), Gunner->GetRocketAmmo(), 0);
	TestFalse(TEXT("not reloading at rest"), Gunner->IsReloading());

	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("R starts a Hydra reload"), Gunner->IsReloading());
	CompletePublicReload(*Gunner, ESkyguardGunshipWeapon::Rockets);
	TestFalse(TEXT("Hydra reload finishes"), Gunner->IsReloading());
	TestEqual(
		TEXT("empty Hydra pods refill to the designed magazine"),
		Gunner->GetRocketAmmo(),
		SkyguardApacheCpgFeel::RocketMagazineSize);

	TestTrue(
		TEXT("wrote a partial Hydra magazine"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Rockets, 4));
	TestEqual(TEXT("Hydra pods are partial"), Gunner->GetRocketAmmo(), 4);
	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("R starts a partial Hydra reload"), Gunner->IsReloading());
	CompletePublicReload(*Gunner, ESkyguardGunshipWeapon::Rockets);
	TestFalse(TEXT("partial Hydra reload finishes"), Gunner->IsReloading());
	TestEqual(
		TEXT("partial Hydra pods refill to the designed magazine"),
		Gunner->GetRocketAmmo(),
		SkyguardApacheCpgFeel::RocketMagazineSize);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheHellfireRailsReloadToMagazineTest,
	"Skyguard52.Apache.HellfireRailsReloadToMagazine",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheHellfireRailsReloadToMagazineTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardApacheReloadStationsTests;

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	Gunner->ApplyLoadout(ESkyguardLoadout::Balanced);
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	TestEqual(
		TEXT("balanced Hellfire magazine is the CPG feel size"),
		Gunner->GetGuidedAmmo(),
		SkyguardApacheCpgFeel::GuidedMagazineSize);
	TestTrue(
		TEXT("wrote empty Hellfire rails"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::GuidedMissile, 0));
	TestEqual(TEXT("Hellfire rails start empty"), Gunner->GetGuidedAmmo(), 0);
	TestFalse(TEXT("not reloading at rest"), Gunner->IsReloading());

	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("R starts a Hellfire reload"), Gunner->IsReloading());
	CompletePublicReload(*Gunner, ESkyguardGunshipWeapon::GuidedMissile);
	TestFalse(TEXT("Hellfire reload finishes"), Gunner->IsReloading());
	TestEqual(
		TEXT("empty Hellfire rails refill to the designed magazine"),
		Gunner->GetGuidedAmmo(),
		SkyguardApacheCpgFeel::GuidedMagazineSize);

	TestTrue(
		TEXT("wrote a partial Hellfire magazine"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::GuidedMissile, 1));
	TestEqual(TEXT("Hellfire rails are partial"), Gunner->GetGuidedAmmo(), 1);
	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("R starts a partial Hellfire reload"), Gunner->IsReloading());
	CompletePublicReload(*Gunner, ESkyguardGunshipWeapon::GuidedMissile);
	TestFalse(TEXT("partial Hellfire reload finishes"), Gunner->IsReloading());
	TestEqual(
		TEXT("partial Hellfire rails refill to the designed magazine"),
		Gunner->GetGuidedAmmo(),
		SkyguardApacheCpgFeel::GuidedMagazineSize);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheHydraAndHellfireReloadIndependentlyTest,
	"Skyguard52.Apache.HydraAndHellfireReloadIndependently",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheHydraAndHellfireReloadIndependentlyTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardApacheReloadStationsTests;

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	Gunner->ApplyLoadout(ESkyguardLoadout::Balanced);
	const int32 HellfireBeforeHydraReload = Gunner->GetGuidedAmmo();
	TestTrue(
		TEXT("wrote empty Hydra pods"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Rockets, 0));
	TestTrue(
		TEXT("wrote a leftover Hellfire"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::GuidedMissile, 1));

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	Gunner->ReloadSelectedWeapon();
	CompletePublicReload(*Gunner, ESkyguardGunshipWeapon::Rockets);
	TestEqual(
		TEXT("Hydra refill uses the designed rocket magazine"),
		Gunner->GetRocketAmmo(),
		SkyguardApacheCpgFeel::RocketMagazineSize);
	TestEqual(
		TEXT("Hydra reload leaves Hellfire rails alone"),
		Gunner->GetGuidedAmmo(),
		1);
	TestTrue(
		TEXT("Hellfire was not the balanced default during the Hydra reload"),
		HellfireBeforeHydraReload != 1);

	const int32 HydraAfterHydraReload = Gunner->GetRocketAmmo();
	TestTrue(
		TEXT("wrote empty Hellfire rails"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::GuidedMissile, 0));
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	Gunner->ReloadSelectedWeapon();
	CompletePublicReload(*Gunner, ESkyguardGunshipWeapon::GuidedMissile);
	TestEqual(
		TEXT("Hellfire refill uses the designed guided magazine"),
		Gunner->GetGuidedAmmo(),
		SkyguardApacheCpgFeel::GuidedMagazineSize);
	TestEqual(
		TEXT("Hellfire reload leaves Hydra pods alone"),
		Gunner->GetRocketAmmo(),
		HydraAfterHydraReload);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheReloadDoesNotInventPastCapTest,
	"Skyguard52.Apache.ReloadDoesNotInventPastCap",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheReloadDoesNotInventPastCapTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardApacheReloadStationsTests;

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	Gunner->ApplyLoadout(ESkyguardLoadout::Balanced);
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	TestEqual(
		TEXT("full Hydra pods sit at the designed cap"),
		Gunner->GetRocketAmmo(),
		SkyguardApacheCpgFeel::RocketMagazineSize);
	Gunner->ReloadSelectedWeapon();
	TestFalse(
		TEXT("full Hydra pods do not start a reload"),
		Gunner->IsReloading());
	TestEqual(
		TEXT("full Hydra reload does not invent past the cap"),
		Gunner->GetRocketAmmo(),
		SkyguardApacheCpgFeel::RocketMagazineSize);

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	TestEqual(
		TEXT("full Hellfire rails sit at the designed cap"),
		Gunner->GetGuidedAmmo(),
		SkyguardApacheCpgFeel::GuidedMagazineSize);
	Gunner->ReloadSelectedWeapon();
	TestFalse(
		TEXT("full Hellfire rails do not start a reload"),
		Gunner->IsReloading());
	TestEqual(
		TEXT("full Hellfire reload does not invent past the cap"),
		Gunner->GetGuidedAmmo(),
		SkyguardApacheCpgFeel::GuidedMagazineSize);

	TestTrue(
		TEXT("wrote empty Hydra pods"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Rockets, 0));
	TestTrue(
		TEXT("wrote a short Hydra reserve"),
		SetReserve(*Gunner, ESkyguardGunshipWeapon::Rockets, 3));
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	Gunner->ReloadSelectedWeapon();
	TestTrue(TEXT("short Hydra reserve still starts a reload"), Gunner->IsReloading());
	CompletePublicReload(*Gunner, ESkyguardGunshipWeapon::Rockets);
	TestEqual(
		TEXT("Hydra reload takes only the remaining reserve"),
		Gunner->GetRocketAmmo(),
		3);
	TestTrue(
		TEXT("short Hydra reserve does not invent a full magazine"),
		Gunner->GetRocketAmmo() < SkyguardApacheCpgFeel::RocketMagazineSize);
	int32 HydraReserve = -1;
	TestTrue(
		TEXT("read Hydra reserve"),
		GetReserve(*Gunner, ESkyguardGunshipWeapon::Rockets, HydraReserve));
	TestEqual(TEXT("Hydra reserve is spent"), HydraReserve, 0);

	TestTrue(
		TEXT("wrote empty Hellfire rails"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::GuidedMissile, 0));
	TestTrue(
		TEXT("wrote a short Hellfire reserve"),
		SetReserve(*Gunner, ESkyguardGunshipWeapon::GuidedMissile, 1));
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	Gunner->ReloadSelectedWeapon();
	CompletePublicReload(*Gunner, ESkyguardGunshipWeapon::GuidedMissile);
	TestEqual(
		TEXT("Hellfire reload takes only the remaining reserve"),
		Gunner->GetGuidedAmmo(),
		1);
	TestTrue(
		TEXT("short Hellfire reserve does not invent a full magazine"),
		Gunner->GetGuidedAmmo() < SkyguardApacheCpgFeel::GuidedMagazineSize);
	int32 HellfireReserve = -1;
	TestTrue(
		TEXT("read Hellfire reserve"),
		GetReserve(*Gunner, ESkyguardGunshipWeapon::GuidedMissile, HellfireReserve));
	TestEqual(TEXT("Hellfire reserve is spent"), HellfireReserve, 0);

	TestTrue(
		TEXT("wrote empty Hydra pods with no reserve"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Rockets, 0));
	TestTrue(
		TEXT("wrote a zero Hydra reserve"),
		SetReserve(*Gunner, ESkyguardGunshipWeapon::Rockets, 0));
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	Gunner->ReloadSelectedWeapon();
	TestFalse(
		TEXT("empty Hydra pods with no reserve do not invent a reload"),
		Gunner->IsReloading());
	TestEqual(TEXT("empty Hydra pods stay empty"), Gunner->GetRocketAmmo(), 0);

	const FSkyguardLoadoutSpec AntiArmor =
		SkyguardResolveLoadout(ESkyguardLoadout::AntiArmor);
	Gunner->ApplyLoadout(ESkyguardLoadout::AntiArmor);
	TestTrue(
		TEXT("anti-armor Hydra magazine is smaller than the default CPG feel"),
		AntiArmor.RocketMagazineSize < SkyguardApacheCpgFeel::RocketMagazineSize);
	TestTrue(
		TEXT("anti-armor Hellfire magazine is larger than the default CPG feel"),
		AntiArmor.GuidedMagazineSize > SkyguardApacheCpgFeel::GuidedMagazineSize);
	TestTrue(
		TEXT("wrote empty anti-armor Hydra pods"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::Rockets, 0));
	TestTrue(
		TEXT("wrote empty anti-armor Hellfire rails"),
		SetReadyAmmo(*Gunner, ESkyguardGunshipWeapon::GuidedMissile, 0));

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	Gunner->ReloadSelectedWeapon();
	CompletePublicReload(*Gunner, ESkyguardGunshipWeapon::Rockets);
	TestEqual(
		TEXT("anti-armor Hydra reload stops at that loadout magazine"),
		Gunner->GetRocketAmmo(),
		AntiArmor.RocketMagazineSize);
	TestTrue(
		TEXT("anti-armor Hydra reload does not invent the default rocket cap"),
		Gunner->GetRocketAmmo() != SkyguardApacheCpgFeel::RocketMagazineSize);

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	Gunner->ReloadSelectedWeapon();
	CompletePublicReload(*Gunner, ESkyguardGunshipWeapon::GuidedMissile);
	TestEqual(
		TEXT("anti-armor Hellfire reload stops at that loadout magazine"),
		Gunner->GetGuidedAmmo(),
		AntiArmor.GuidedMagazineSize);
	return true;
}

#endif
