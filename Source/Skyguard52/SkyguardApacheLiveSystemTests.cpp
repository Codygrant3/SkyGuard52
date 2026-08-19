#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardApacheAircraft.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheFindNearestLiveSystemAfterTwoKillsTest,
	"Skyguard52.Apache.FindNearestLiveSystemAfterTwoKills",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheFindNearestLiveSystemAfterTwoKillsTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheLiveSystemTwoKillWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardApacheAircraft* Apache =
		World->SpawnActor<ASkyguardApacheAircraft>();
	TestNotNull(TEXT("apache"), Apache);
	if (!Apache)
	{
		World->DestroyWorld(false);
		return false;
	}

	TestTrue(
		TEXT("healthy CPG priority is Sensor"),
		Apache->FindNearestLiveSystem() == ESkyguardApacheSystem::Sensor);
	TestFalse(
		TEXT("Sensor starts live"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Sensor));
	TestFalse(
		TEXT("ChinTurret starts live"),
		Apache->IsSystemDown(ESkyguardApacheSystem::ChinTurret));
	TestFalse(
		TEXT("Engines start live"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Engines));
	TestFalse(
		TEXT("Rotor starts live"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Rotor));
	TestFalse(
		TEXT("Canopy starts live"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Canopy));

	const float HullBefore = Apache->GetDamageFraction();
	Apache->ApplySystemHit(ESkyguardApacheSystem::Sensor, 999.f);
	Apache->ApplySystemHit(ESkyguardApacheSystem::ChinTurret, 999.f);

	TestTrue(
		TEXT("Sensor is down"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Sensor));
	TestTrue(
		TEXT("ChinTurret is down"),
		Apache->IsSystemDown(ESkyguardApacheSystem::ChinTurret));
	TestFalse(
		TEXT("Engines stay live after Sensor and ChinTurret die"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Engines));
	TestFalse(
		TEXT("Rotor stays live after Sensor and ChinTurret die"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Rotor));
	TestFalse(
		TEXT("Canopy stays live after Sensor and ChinTurret die"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Canopy));
	TestTrue(
		TEXT("priority skips dead Sensor and ChinTurret"),
		Apache->FindNearestLiveSystem() == ESkyguardApacheSystem::Engines);
	TestTrue(
		TEXT("FindNearestLiveSystem is not Sensor after TADS dies"),
		Apache->FindNearestLiveSystem() != ESkyguardApacheSystem::Sensor);
	TestTrue(
		TEXT("FindNearestLiveSystem is not ChinTurret after chin dies"),
		Apache->FindNearestLiveSystem() != ESkyguardApacheSystem::ChinTurret);
	TestTrue(
		TEXT("system kills do not move the hull bar"),
		FMath::IsNearlyEqual(Apache->GetDamageFraction(), HullBefore));

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheFindNearestLiveSystemAllDownReturnsCanopyTest,
	"Skyguard52.Apache.FindNearestLiveSystemAllDownReturnsCanopy",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheFindNearestLiveSystemAllDownReturnsCanopyTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheLiveSystemAllDownWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardApacheAircraft* Apache =
		World->SpawnActor<ASkyguardApacheAircraft>();
	TestNotNull(TEXT("apache"), Apache);
	if (!Apache)
	{
		World->DestroyWorld(false);
		return false;
	}

	Apache->ApplyDamage(40.f);
	const float HullAfterBarHit = Apache->GetDamageFraction();
	TestTrue(TEXT("hull bar moved on its own"), HullAfterBarHit > 0.f);
	TestTrue(
		TEXT("hull hit does not steal CPG priority from Sensor"),
		Apache->FindNearestLiveSystem() == ESkyguardApacheSystem::Sensor);

	Apache->ApplySystemHit(ESkyguardApacheSystem::Sensor, 999.f);
	Apache->ApplySystemHit(ESkyguardApacheSystem::ChinTurret, 999.f);
	Apache->ApplySystemHit(ESkyguardApacheSystem::Engines, 999.f);
	Apache->ApplySystemHit(ESkyguardApacheSystem::Rotor, 999.f);
	Apache->ApplySystemHit(ESkyguardApacheSystem::Canopy, 999.f);

	TestTrue(
		TEXT("Sensor down"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Sensor));
	TestTrue(
		TEXT("ChinTurret down"),
		Apache->IsSystemDown(ESkyguardApacheSystem::ChinTurret));
	TestTrue(
		TEXT("Engines down"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Engines));
	TestTrue(
		TEXT("Rotor down"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Rotor));
	TestTrue(
		TEXT("Canopy down"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Canopy));
	TestTrue(
		TEXT("all-down returns last remaining Canopy, not a hull sentinel"),
		Apache->FindNearestLiveSystem() == ESkyguardApacheSystem::Canopy);
	TestTrue(
		TEXT("all-down still leaves the hull bar untouched by system hits"),
		FMath::IsNearlyEqual(Apache->GetDamageFraction(), HullAfterBarHit));

	World->DestroyWorld(false);
	return true;
}

#endif
