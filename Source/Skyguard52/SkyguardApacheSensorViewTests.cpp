#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardApacheAircraft.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace
{
	/** Hunt-sight thermal is available only above this public quality floor. */
	constexpr float ThermalLiveFloor = 0.35f;

	/** Sensor integrity starts at 50; this is enough to zero TADS. */
	constexpr float KillTadsHit = 999.f;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheSensorViewGatedByTadsIntegrityTest,
	"Skyguard52.Apache.SensorViewGatedByTadsIntegrity",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheSensorViewGatedByTadsIntegrityTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheSensorViewWorld"));
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

	TestTrue(TEXT("TADS starts live"), Apache->IsSensorLive());
	TestFalse(
		TEXT("sensor view starts off"),
		Apache->IsSensorViewActive());

	Apache->SetSensorView(true);
	TestTrue(
		TEXT("SetSensorView reports active while TADS is live"),
		Apache->IsSensorViewActive());
	TestTrue(
		TEXT("live TADS still offers a thermal hunt sight"),
		Apache->IsThermalAvailable());

	Apache->ApplySystemHit(ESkyguardApacheSystem::Sensor, KillTadsHit);
	TestFalse(TEXT("dead TADS is not live"), Apache->IsSensorLive());
	TestTrue(
		TEXT("dead TADS drops thermal or sits at/under the live floor"),
		!Apache->IsThermalAvailable() ||
			Apache->GetSensorQuality() <= ThermalLiveFloor);
	TestFalse(
		TEXT("killing TADS drops an engaged sensor view"),
		Apache->IsSensorViewActive());

	Apache->SetSensorView(true);
	TestFalse(
		TEXT("SetSensorView cannot pretend a dead TADS is still a live hunt sight"),
		Apache->IsSensorViewActive());

	World->DestroyWorld(false);
	return true;
}

#endif
