#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardApacheAircraft.h"
#include "SkyguardRuntimeMeshCatalog.h"

#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardApacheOwnShipSystemHitTests
{
	ASkyguardApacheAircraft* SpawnApache(UWorld*& OutWorld, const TCHAR* WorldName)
	{
		OutWorld = UWorld::CreateWorld(EWorldType::Game, false, WorldName);
		if (!OutWorld)
		{
			return nullptr;
		}
		return OutWorld->SpawnActor<ASkyguardApacheAircraft>();
	}

	void DestroyWorld(UWorld* World)
	{
		if (World)
		{
			World->DestroyWorld(false);
		}
	}

	bool SlotPreferredIsEmpty(const FSkyguardMeshBindSlot& Slot)
	{
		return !Slot.Preferred.ToSoftObjectPath().IsValid();
	}

	bool ApacheCatalogPreferredStaysEmpty()
	{
		USkyguardRuntimeMeshCatalog* Catalog =
			NewObject<USkyguardRuntimeMeshCatalog>();
		if (!Catalog)
		{
			return false;
		}
		Catalog->EnsureDefaultSlots();

		const FSkyguardMeshBindSlot* Airframe =
			Catalog->FindSlot(TEXT("Apache.Airframe"));
		const FSkyguardMeshBindSlot* Cockpit =
			Catalog->FindSlot(TEXT("Gunner.Cockpit"));
		if (!Airframe || !Cockpit)
		{
			return false;
		}
		if (!SlotPreferredIsEmpty(*Airframe) || !SlotPreferredIsEmpty(*Cockpit))
		{
			return false;
		}

		for (const FSkyguardMeshBindSlot& Slot :
			USkyguardRuntimeMeshCatalog::GetCodeDefaultSlots())
		{
			const FString Id = Slot.SlotId.ToString();
			if (!Id.StartsWith(TEXT("Apache.")) && Id != TEXT("Gunner.Cockpit"))
			{
				continue;
			}
			if (!SlotPreferredIsEmpty(Slot))
			{
				return false;
			}
		}
		return true;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheSensorHitDropsSensorPlayWithoutHullBarTest,
	"Skyguard52.Apache.OwnShip.SensorHitDropsSensorPlayWithoutHullBar",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheSensorHitDropsSensorPlayWithoutHullBarTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = nullptr;
	ASkyguardApacheAircraft* Apache =
		SkyguardApacheOwnShipSystemHitTests::SpawnApache(
			World,
			TEXT("SkyguardApacheOwnShipSensorWorld"));
	TestNotNull(TEXT("world"), World);
	TestNotNull(TEXT("apache"), Apache);
	if (!World || !Apache)
	{
		SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
		return false;
	}

	const float HullBefore = Apache->CurrentIntegrity;
	TestTrue(TEXT("TADS starts live"), Apache->IsSensorLive());
	TestTrue(
		TEXT("sensor quality starts full"),
		FMath::IsNearlyEqual(Apache->GetSensorQuality(), 1.f, 0.01f));
	TestTrue(TEXT("thermal starts available"), Apache->IsThermalAvailable());
	TestTrue(
		TEXT("hull starts intact"),
		FMath::IsNearlyZero(Apache->GetDamageFraction()));

	const float SameAmountAsHullSample = 35.f;
	Apache->ApplySystemHit(ESkyguardApacheSystem::Sensor, SameAmountAsHullSample);
	TestTrue(
		TEXT("partial TADS hit drops quality"),
		Apache->GetSensorQuality() < 1.f);
	TestTrue(
		TEXT("sensor hit does not move CurrentIntegrity"),
		FMath::IsNearlyEqual(Apache->CurrentIntegrity, HullBefore, 0.01f));

	Apache->ApplySystemHit(ESkyguardApacheSystem::Sensor, 999.f);
	TestFalse(TEXT("killing TADS drops IsSensorLive"), Apache->IsSensorLive());
	TestTrue(
		TEXT("killing TADS drops GetSensorQuality"),
		FMath::IsNearlyZero(Apache->GetSensorQuality()));
	TestFalse(
		TEXT("killing TADS drops IsThermalAvailable"),
		Apache->IsThermalAvailable());
	TestTrue(
		TEXT("dead TADS still leaves hull CurrentIntegrity untouched"),
		FMath::IsNearlyEqual(Apache->CurrentIntegrity, HullBefore, 0.01f));
	TestTrue(
		TEXT("dead TADS is not a hull bar"),
		FMath::IsNearlyZero(Apache->GetDamageFraction()));

	Apache->ApplyDamage(SameAmountAsHullSample);
	TestTrue(
		TEXT("ApplyDamage is the hull bar"),
		Apache->CurrentIntegrity < HullBefore);
	TestTrue(
		TEXT("ApplyDamage subtracts CurrentIntegrity"),
		FMath::IsNearlyEqual(
			Apache->CurrentIntegrity,
			HullBefore - SameAmountAsHullSample,
			0.01f));
	TestTrue(
		TEXT("hull fraction moves only through ApplyDamage"),
		Apache->GetDamageFraction() > KINDA_SMALL_NUMBER);

	SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheCanopyHitCracksGlassWithoutHullBarTest,
	"Skyguard52.Apache.OwnShip.CanopyHitCracksGlassWithoutHullBar",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheCanopyHitCracksGlassWithoutHullBarTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = nullptr;
	ASkyguardApacheAircraft* Apache =
		SkyguardApacheOwnShipSystemHitTests::SpawnApache(
			World,
			TEXT("SkyguardApacheOwnShipCanopyWorld"));
	TestNotNull(TEXT("world"), World);
	TestNotNull(TEXT("apache"), Apache);
	if (!World || !Apache)
	{
		SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
		return false;
	}

	const float HullBefore = Apache->CurrentIntegrity;
	TestFalse(TEXT("glass starts clear"), Apache->IsCanopyGlassCracked());

	Apache->ApplySystemHit(ESkyguardApacheSystem::Canopy, 8.f);
	TestTrue(TEXT("canopy hit sets IsCanopyGlassCracked"), Apache->IsCanopyGlassCracked());
	TestTrue(TEXT("cracked glass leaves TADS live"), Apache->IsSensorLive());
	TestFalse(TEXT("cracked glass leaves engines up"), Apache->AreEnginesDown());
	TestFalse(TEXT("cracked glass leaves chin up"), Apache->IsChinTurretDown());
	TestFalse(TEXT("cracked glass leaves rotor up"), Apache->IsRotorDown());
	TestTrue(
		TEXT("canopy hit does not move CurrentIntegrity"),
		FMath::IsNearlyEqual(Apache->CurrentIntegrity, HullBefore, 0.01f));
	TestTrue(
		TEXT("canopy hit is not hull integrity"),
		FMath::IsNearlyZero(Apache->GetDamageFraction()));

	SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheEngineHitSetsDownAndPowerScaleWithoutPreferredTest,
	"Skyguard52.Apache.OwnShip.EngineHitSetsDownAndPowerScaleWithoutPreferred",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheEngineHitSetsDownAndPowerScaleWithoutPreferredTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = nullptr;
	ASkyguardApacheAircraft* Apache =
		SkyguardApacheOwnShipSystemHitTests::SpawnApache(
			World,
			TEXT("SkyguardApacheOwnShipEngineWorld"));
	TestNotNull(TEXT("world"), World);
	TestNotNull(TEXT("apache"), Apache);
	if (!World || !Apache)
	{
		SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
		return false;
	}

	const float HullBefore = Apache->CurrentIntegrity;
	TestFalse(TEXT("engines start up"), Apache->AreEnginesDown());
	TestTrue(
		TEXT("engine power starts full"),
		FMath::IsNearlyEqual(Apache->GetEnginePowerScale(), 1.f, 0.01f));

	Apache->ApplySystemHit(ESkyguardApacheSystem::Engines, 999.f);
	TestTrue(TEXT("engine hit sets AreEnginesDown"), Apache->AreEnginesDown());
	TestTrue(
		TEXT("engine hit scales GetEnginePowerScale down"),
		Apache->GetEnginePowerScale() < 1.f);
	TestTrue(
		TEXT("engine limp is not a crash"),
		Apache->GetEnginePowerScale() > 0.2f);
	TestTrue(
		TEXT("engine hit does not move CurrentIntegrity"),
		FMath::IsNearlyEqual(Apache->CurrentIntegrity, HullBefore, 0.01f));
	TestTrue(
		TEXT("engine hit does not fill catalog Preferred"),
		SkyguardApacheOwnShipSystemHitTests::ApacheCatalogPreferredStaysEmpty());

	SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheChinTurretHitSetsDownAndFireScaleWithoutPreferredTest,
	"Skyguard52.Apache.OwnShip.ChinTurretHitSetsDownAndFireScaleWithoutPreferred",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheChinTurretHitSetsDownAndFireScaleWithoutPreferredTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = nullptr;
	ASkyguardApacheAircraft* Apache =
		SkyguardApacheOwnShipSystemHitTests::SpawnApache(
			World,
			TEXT("SkyguardApacheOwnShipChinWorld"));
	TestNotNull(TEXT("world"), World);
	TestNotNull(TEXT("apache"), Apache);
	if (!World || !Apache)
	{
		SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
		return false;
	}

	const float HullBefore = Apache->CurrentIntegrity;
	TestFalse(TEXT("chin starts up"), Apache->IsChinTurretDown());
	TestTrue(
		TEXT("chin fire starts full"),
		FMath::IsNearlyEqual(Apache->GetChinFireScale(), 1.f, 0.01f));

	Apache->ApplySystemHit(ESkyguardApacheSystem::ChinTurret, 999.f);
	TestTrue(TEXT("chin hit sets IsChinTurretDown"), Apache->IsChinTurretDown());
	TestTrue(
		TEXT("chin hit scales GetChinFireScale down"),
		Apache->GetChinFireScale() < 0.15f);
	TestTrue(
		TEXT("chin hit does not move CurrentIntegrity"),
		FMath::IsNearlyEqual(Apache->CurrentIntegrity, HullBefore, 0.01f));
	TestTrue(
		TEXT("chin hit does not fill catalog Preferred"),
		SkyguardApacheOwnShipSystemHitTests::ApacheCatalogPreferredStaysEmpty());

	SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheRotorHitSetsDownAndPowerScaleWithoutPreferredTest,
	"Skyguard52.Apache.OwnShip.RotorHitSetsDownAndPowerScaleWithoutPreferred",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheRotorHitSetsDownAndPowerScaleWithoutPreferredTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = nullptr;
	ASkyguardApacheAircraft* Apache =
		SkyguardApacheOwnShipSystemHitTests::SpawnApache(
			World,
			TEXT("SkyguardApacheOwnShipRotorWorld"));
	TestNotNull(TEXT("world"), World);
	TestNotNull(TEXT("apache"), Apache);
	if (!World || !Apache)
	{
		SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
		return false;
	}

	const float HullBefore = Apache->CurrentIntegrity;
	TestFalse(TEXT("rotor starts up"), Apache->IsRotorDown());
	TestTrue(
		TEXT("rotor power starts full"),
		FMath::IsNearlyEqual(Apache->GetRotorPowerScale(), 1.f, 0.01f));

	Apache->ApplySystemHit(ESkyguardApacheSystem::Rotor, 999.f);
	TestTrue(TEXT("rotor hit sets IsRotorDown"), Apache->IsRotorDown());
	TestTrue(
		TEXT("rotor hit scales GetRotorPowerScale down"),
		Apache->GetRotorPowerScale() < 1.f);
	TestTrue(
		TEXT("rotor limp is not an insta-kill"),
		Apache->GetRotorPowerScale() > 0.2f);
	TestTrue(
		TEXT("rotor hit does not move CurrentIntegrity"),
		FMath::IsNearlyEqual(Apache->CurrentIntegrity, HullBefore, 0.01f));
	TestTrue(
		TEXT("rotor hit does not fill catalog Preferred"),
		SkyguardApacheOwnShipSystemHitTests::ApacheCatalogPreferredStaysEmpty());

	SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheHullApplyDamageRemainsSeparateBarTest,
	"Skyguard52.Apache.OwnShip.HullApplyDamageRemainsSeparateBar",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheHullApplyDamageRemainsSeparateBarTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = nullptr;
	ASkyguardApacheAircraft* Apache =
		SkyguardApacheOwnShipSystemHitTests::SpawnApache(
			World,
			TEXT("SkyguardApacheOwnShipHullWorld"));
	TestNotNull(TEXT("world"), World);
	TestNotNull(TEXT("apache"), Apache);
	if (!World || !Apache)
	{
		SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
		return false;
	}

	const float HullBefore = Apache->CurrentIntegrity;
	TestTrue(
		TEXT("starts undamaged"),
		FMath::IsNearlyZero(Apache->GetDamageFraction()));

	Apache->ApplyDamage(Apache->MaxIntegrity * 0.25f);
	TestTrue(
		TEXT("hull fraction moves"),
		FMath::IsNearlyEqual(Apache->GetDamageFraction(), 0.25f, 0.01f));
	TestTrue(
		TEXT("hull CurrentIntegrity dropped"),
		Apache->CurrentIntegrity < HullBefore);
	TestTrue(TEXT("hull hit leaves TADS live"), Apache->IsSensorLive());
	TestTrue(
		TEXT("hull hit leaves sensor quality full"),
		FMath::IsNearlyEqual(Apache->GetSensorQuality(), 1.f, 0.01f));
	TestTrue(TEXT("hull hit leaves thermal available"), Apache->IsThermalAvailable());
	TestFalse(TEXT("hull hit does not crack glass"), Apache->IsCanopyGlassCracked());
	TestFalse(TEXT("hull hit leaves engines up"), Apache->AreEnginesDown());
	TestFalse(TEXT("hull hit leaves chin up"), Apache->IsChinTurretDown());
	TestFalse(TEXT("hull hit leaves rotor up"), Apache->IsRotorDown());
	TestTrue(
		TEXT("hull hit leaves engine scale full"),
		FMath::IsNearlyEqual(Apache->GetEnginePowerScale(), 1.f, 0.01f));
	TestTrue(
		TEXT("hull hit leaves chin fire full"),
		FMath::IsNearlyEqual(Apache->GetChinFireScale(), 1.f, 0.01f));
	TestTrue(
		TEXT("hull hit leaves rotor scale full"),
		FMath::IsNearlyEqual(Apache->GetRotorPowerScale(), 1.f, 0.01f));
	TestTrue(
		TEXT("hull bar does not fill catalog Preferred"),
		SkyguardApacheOwnShipSystemHitTests::ApacheCatalogPreferredStaysEmpty());

	SkyguardApacheOwnShipSystemHitTests::DestroyWorld(World);
	return true;
}

#endif
