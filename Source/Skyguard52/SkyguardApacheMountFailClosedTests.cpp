#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardApacheAircraft.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardApacheAircraftEmptyFailClosedTests.cpp.
// Constructor sockets/mounts via public getters only.
// NewObject on the transient package. No world, no SpawnActor.
// Does not call AimChinTurret, SetRotorPower, IssuePilotCommand,
// SetOrbitFocus, FaceWorldLocation, SetSensorView,
// SetFirstPersonInterior, SetDirectFlightInput, ApplyDamage,
// ApplySystemHit, ApplyHit, Tick, or BeginPlay.
// Does not duplicate empty-director Pursuit / confirmation /
// speed / damage-fraction / system-down assertions.
// No Gunner / Yak / Igla / rifle live copy.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheMountFailClosedTest,
	"Skyguard52.Apache.Mount.FailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheMountFailClosedTest::RunTest(const FString& Parameters)
{
	ASkyguardApacheAircraft* Apache =
		NewObject<ASkyguardApacheAircraft>(GetTransientPackage());
	TestNotNull(TEXT("NewObject apache constructs"), Apache);
	if (!Apache)
	{
		return false;
	}

	TestNotNull(
		TEXT("NewObject GetGunnerMount is non-null"),
		Apache->GetGunnerMount());
	TestNotNull(
		TEXT("NewObject GetPilotMount is non-null"),
		Apache->GetPilotMount());
	TestNotNull(
		TEXT("NewObject GetEyeMount is non-null"),
		Apache->GetEyeMount());
	TestNotNull(
		TEXT("NewObject GetWeaponMount is non-null"),
		Apache->GetWeaponMount());
	TestNotNull(
		TEXT("NewObject GetChinTurret is non-null"),
		Apache->GetChinTurret());
	TestNotNull(
		TEXT("NewObject GetSensorTurret is non-null"),
		Apache->GetSensorTurret());

	return true;
}

#endif
