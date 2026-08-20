#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardDrone.h"

#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardDroneThreatKindTests
{
	UWorld* MakeGameWorld(const TCHAR* Name)
	{
		return UWorld::CreateWorld(EWorldType::Game, false, Name);
	}

	void TearDown(UWorld* World)
	{
		if (World)
		{
			World->DestroyWorld(false);
		}
	}

	ASkyguardDrone* SpawnDrone(UWorld* World, const FVector& Location)
	{
		if (!World)
		{
			return nullptr;
		}
		return World->SpawnActor<ASkyguardDrone>(Location, FRotator::ZeroRotator);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardDroneConfigureThreatPublicApiTest,
	"Skyguard52.Drone.ThreatKind.ConfigureThreatPublicApi",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDroneConfigureThreatPublicApiTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardDroneThreatKindTests;

	UWorld* World = MakeGameWorld(TEXT("SkyguardDroneThreatKindWorld"));
	TestNotNull(TEXT("Game world is created"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardDrone* Fast = SpawnDrone(World, FVector::ZeroVector);
	ASkyguardDrone* Heavy = SpawnDrone(World, FVector(200.f, 0.f, 0.f));
	ASkyguardDrone* Armor = SpawnDrone(World, FVector(400.f, 0.f, 0.f));
	ASkyguardDrone* Boat = SpawnDrone(World, FVector(600.f, 0.f, 0.f));
	ASkyguardDrone* Scout = SpawnDrone(World, FVector(800.f, 0.f, 0.f));
	TestNotNull(TEXT("FastAttacker drone spawns"), Fast);
	TestNotNull(TEXT("HeavyAttacker drone spawns"), Heavy);
	TestNotNull(TEXT("GroundArmor drone spawns"), Armor);
	TestNotNull(TEXT("FastBoat drone spawns"), Boat);
	TestNotNull(TEXT("RotorScout drone spawns"), Scout);
	if (!Fast || !Heavy || !Armor || !Boat || !Scout)
	{
		TearDown(World);
		return false;
	}

	Fast->ConfigureThreat(ESkyguardThreatKind::FastAttacker);
	TestEqual(
		TEXT("ConfigureThreat(FastAttacker) stores FastAttacker"),
		Fast->GetThreatKind(),
		ESkyguardThreatKind::FastAttacker);
	TestFalse(
		TEXT("FastAttacker IsHeavyTarget is false (bHeavy = Kind != FastAttacker)"),
		Fast->IsHeavyTarget());
	TestEqual(
		TEXT("FastAttacker default light MaxHealth is 34"),
		Fast->MaxHealth,
		34.f);
	TestFalse(
		TEXT("FastAttacker IsMissileLockEligible is false at default light health"),
		Fast->IsMissileLockEligible());

	Fast->MaxHealth = 80.f;
	TestTrue(
		TEXT("FastAttacker IsMissileLockEligible is true when MaxHealth >= 80"),
		Fast->IsMissileLockEligible());
	Fast->MaxHealth = 34.f;
	TestFalse(
		TEXT("FastAttacker IsMissileLockEligible is false again at MaxHealth 34"),
		Fast->IsMissileLockEligible());

	Heavy->ConfigureThreat(ESkyguardThreatKind::HeavyAttacker);
	TestEqual(
		TEXT("ConfigureThreat(HeavyAttacker) stores HeavyAttacker"),
		Heavy->GetThreatKind(),
		ESkyguardThreatKind::HeavyAttacker);
	TestTrue(
		TEXT("HeavyAttacker IsHeavyTarget is true"),
		Heavy->IsHeavyTarget());
	TestTrue(
		TEXT("HeavyAttacker IsMissileLockEligible is true"),
		Heavy->IsMissileLockEligible());

	Armor->ConfigureThreat(ESkyguardThreatKind::GroundArmor);
	Boat->ConfigureThreat(ESkyguardThreatKind::FastBoat);
	Scout->ConfigureThreat(ESkyguardThreatKind::RotorScout);

	TestEqual(
		TEXT("ConfigureThreat(GroundArmor) stores GroundArmor"),
		Armor->GetThreatKind(),
		ESkyguardThreatKind::GroundArmor);
	TestTrue(TEXT("GroundArmor IsHeavyTarget is true"), Armor->IsHeavyTarget());
	TestTrue(
		TEXT("GroundArmor IsMissileLockEligible is true"),
		Armor->IsMissileLockEligible());

	TestEqual(
		TEXT("ConfigureThreat(FastBoat) stores FastBoat"),
		Boat->GetThreatKind(),
		ESkyguardThreatKind::FastBoat);
	TestTrue(TEXT("FastBoat IsHeavyTarget is true"), Boat->IsHeavyTarget());
	TestTrue(
		TEXT("FastBoat IsMissileLockEligible is true"),
		Boat->IsMissileLockEligible());

	TestEqual(
		TEXT("ConfigureThreat(RotorScout) stores RotorScout"),
		Scout->GetThreatKind(),
		ESkyguardThreatKind::RotorScout);
	TestTrue(TEXT("RotorScout IsHeavyTarget is true"), Scout->IsHeavyTarget());
	TestTrue(
		TEXT("RotorScout IsMissileLockEligible is true"),
		Scout->IsMissileLockEligible());

	TearDown(World);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardDroneMakeHullBindSlotPreferredStaysEmptyTest,
	"Skyguard52.Drone.ThreatKind.MakeHullBindSlotPreferredStaysEmpty",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDroneMakeHullBindSlotPreferredStaysEmptyTest::RunTest(
	const FString& Parameters)
{
	const FSkyguardMeshBindSlot HullSlot = ASkyguardDrone::MakeHullBindSlot();
	TestEqual(
		TEXT("hull slot id"),
		HullSlot.SlotId,
		FName(TEXT("Drone.Hull")));
	TestTrue(
		TEXT("MakeHullBindSlot Preferred stays empty (ProxyFallback bind contract)"),
		HullSlot.Preferred.IsNull());
	TestFalse(
		TEXT("MakeHullBindSlot ProxyFallback is set"),
		HullSlot.ProxyFallback.IsNull());
	return true;
}

#endif
