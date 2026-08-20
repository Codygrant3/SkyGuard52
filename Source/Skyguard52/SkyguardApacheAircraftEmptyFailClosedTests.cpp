#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardApacheAircraft.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardApacheAircraftTests.cpp.
// Remaining empty-director NewObject public getters only, before
// ApplyDamage / ApplySystemHit / IssuePilotCommand / SetSensorView.
// Existing SkyguardApacheAircraftTests.cpp,
// SkyguardApacheOwnShipSystemHitTests.cpp,
// SkyguardApacheLiveSystemTests.cpp, and
// SkyguardApacheChinMuzzleTests.cpp already cover hits,
// live-system routing, and chin muzzle.
// This file is undamaged empty-director defaults.
// NewObject only. No world, no Gunner / Yak / Igla / rifle.
// Does not call ApplyDamage, ApplySystemHit, ApplyHit,
// IssuePilotCommand, SetSensorView, SetDirectFlightInput,
// or AimChinTurret.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheAircraftEmptyFailClosedTest,
	"Skyguard52.Apache.Aircraft.EmptyFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheAircraftEmptyFailClosedTest::RunTest(const FString& Parameters)
{
	ASkyguardApacheAircraft* Apache =
		NewObject<ASkyguardApacheAircraft>(GetTransientPackage());
	TestNotNull(TEXT("NewObject empty apache constructs"), Apache);
	if (!Apache)
	{
		return false;
	}

	TestTrue(
		TEXT("Constructor enables PrimaryActorTick"),
		Apache->PrimaryActorTick.bCanEverTick);

	TestEqual(
		TEXT("NewObject GetPilotCommand is Pursuit"),
		Apache->GetPilotCommand(),
		ESkyguardPilotCommand::Pursuit);
	TestEqual(
		TEXT("NewObject GetPilotConfirmationsIssued is 0"),
		Apache->GetPilotConfirmationsIssued(),
		0);

	TestEqual(
		TEXT("NewObject GetForwardSpeed is 900"),
		Apache->GetForwardSpeed(),
		900.f);

	TestEqual(
		TEXT("NewObject MaxIntegrity is 140"),
		Apache->MaxIntegrity,
		140.f);
	TestEqual(
		TEXT("NewObject CurrentIntegrity is 140"),
		Apache->CurrentIntegrity,
		140.f);
	TestEqual(
		TEXT("NewObject CurrentIntegrity equals MaxIntegrity"),
		Apache->CurrentIntegrity,
		Apache->MaxIntegrity);
	TestEqual(
		TEXT("NewObject GetDamageFraction is 0"),
		Apache->GetDamageFraction(),
		0.f);

	TestTrue(TEXT("NewObject IsSensorLive is true"), Apache->IsSensorLive());
	TestFalse(
		TEXT("NewObject IsSensorViewActive is false"),
		Apache->IsSensorViewActive());
	TestFalse(
		TEXT("NewObject IsCanopyGlassCracked is false"),
		Apache->IsCanopyGlassCracked());

	TestFalse(TEXT("NewObject AreEnginesDown is false"), Apache->AreEnginesDown());
	TestFalse(
		TEXT("NewObject IsChinTurretDown is false"),
		Apache->IsChinTurretDown());
	TestFalse(TEXT("NewObject IsRotorDown is false"), Apache->IsRotorDown());

	TestFalse(
		TEXT("NewObject IsSystemDown(Sensor) is false"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Sensor));
	TestFalse(
		TEXT("NewObject IsSystemDown(Canopy) is false"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Canopy));
	TestFalse(
		TEXT("NewObject IsSystemDown(Engines) is false"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Engines));
	TestFalse(
		TEXT("NewObject IsSystemDown(ChinTurret) is false"),
		Apache->IsSystemDown(ESkyguardApacheSystem::ChinTurret));
	TestFalse(
		TEXT("NewObject IsSystemDown(Rotor) is false"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Rotor));

	return true;
}

#endif
