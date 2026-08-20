#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGunFireCameraShake.h"

#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGunFireCameraShakeConstructorDefaultsTest,
	"Skyguard52.Apache.Cpg.GunFireCameraShakeConstructorDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGunFireCameraShakeConstructorDefaultsTest::RunTest(
	const FString& Parameters)
{
	// Constructor public defaults only. Do not play the shake or spawn a
	// camera / Gunner. Apache CPG 30 mm muzzle recoil shake.
	const USkyguardGunFireCameraShake* Shake =
		NewObject<USkyguardGunFireCameraShake>();
	TestNotNull(
		TEXT("Apache CPG 30 mm muzzle recoil shake object is created"),
		Shake);
	if (!Shake)
	{
		return false;
	}

	TestEqual(
		TEXT("Apache CPG 30 mm muzzle recoil shake is not single-instance"),
		static_cast<bool>(Shake->bSingleInstance),
		false);
	TestEqual(
		TEXT("Apache CPG 30 mm OscillationDuration"),
		Shake->OscillationDuration,
		0.12f);
	TestEqual(
		TEXT("Apache CPG 30 mm OscillationBlendInTime"),
		Shake->OscillationBlendInTime,
		0.02f);
	TestEqual(
		TEXT("Apache CPG 30 mm OscillationBlendOutTime"),
		Shake->OscillationBlendOutTime,
		0.08f);

	TestEqual(
		TEXT("Apache CPG 30 mm RotOscillation.Pitch.Amplitude"),
		Shake->RotOscillation.Pitch.Amplitude,
		0.4f);
	TestEqual(
		TEXT("Apache CPG 30 mm RotOscillation.Pitch.Frequency"),
		Shake->RotOscillation.Pitch.Frequency,
		28.f);
	TestEqual(
		TEXT("Apache CPG 30 mm RotOscillation.Yaw.Amplitude"),
		Shake->RotOscillation.Yaw.Amplitude,
		0.18f);
	TestEqual(
		TEXT("Apache CPG 30 mm RotOscillation.Yaw.Frequency"),
		Shake->RotOscillation.Yaw.Frequency,
		22.f);
	TestEqual(
		TEXT("Apache CPG 30 mm RotOscillation.Roll.Amplitude"),
		Shake->RotOscillation.Roll.Amplitude,
		0.08f);
	TestEqual(
		TEXT("Apache CPG 30 mm RotOscillation.Roll.Frequency"),
		Shake->RotOscillation.Roll.Frequency,
		18.f);

	TestEqual(
		TEXT("Apache CPG 30 mm LocOscillation.X.Amplitude"),
		Shake->LocOscillation.X.Amplitude,
		1.8f);
	TestEqual(
		TEXT("Apache CPG 30 mm LocOscillation.X.Frequency"),
		Shake->LocOscillation.X.Frequency,
		30.f);
	TestEqual(
		TEXT("Apache CPG 30 mm LocOscillation.Z.Amplitude"),
		Shake->LocOscillation.Z.Amplitude,
		0.6f);
	TestEqual(
		TEXT("Apache CPG 30 mm LocOscillation.Z.Frequency"),
		Shake->LocOscillation.Z.Frequency,
		24.f);

	return true;
}

#endif
