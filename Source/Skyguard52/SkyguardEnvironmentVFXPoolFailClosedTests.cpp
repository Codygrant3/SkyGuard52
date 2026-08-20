#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardEnvironmentVFXPoolComponent.h"

#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardEnvironmentVFXPoolFailClosedTest,
	"Skyguard52.Environment.VFX.PoolFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardEnvironmentVFXPoolFailClosedTest::RunTest(
	const FString& Parameters)
{
	USkyguardEnvironmentVFXPoolComponent* Pool =
		NewObject<USkyguardEnvironmentVFXPoolComponent>(GetTransientPackage());
	TestNotNull(TEXT("Ownerless environment VFX pool can be NewObject-constructed"), Pool);
	if (!Pool)
	{
		return false;
	}

	TestFalse(
		TEXT("Constructor disables component tick"),
		Pool->PrimaryComponentTick.bCanEverTick);
	TestEqual(
		TEXT("Default PoolCapacity is 12"),
		Pool->PoolCapacity,
		12);
	TestEqual(
		TEXT("NewObject pool has allocated nothing"),
		Pool->GetAllocatedPoolSize(),
		0);
	TestEqual(
		TEXT("NewObject pool has no activations"),
		Pool->GetActivationCount(),
		0);

	TestFalse(
		TEXT("Ownerless Smoke activate fails closed"),
		Pool->ActivatePooledEffect(
			ESkyguardEnvironmentVFXType::Smoke,
			FTransform::Identity));
	TestFalse(
		TEXT("Ownerless Fire activate fails closed"),
		Pool->ActivatePooledEffect(
			ESkyguardEnvironmentVFXType::Fire,
			FTransform::Identity));
	TestFalse(
		TEXT("Ownerless Sparks activate fails closed"),
		Pool->ActivatePooledEffect(
			ESkyguardEnvironmentVFXType::Sparks,
			FTransform::Identity));
	TestFalse(
		TEXT("Ownerless Explosion activate fails closed"),
		Pool->ActivatePooledEffect(
			ESkyguardEnvironmentVFXType::Explosion,
			FTransform::Identity));

	TestEqual(
		TEXT("Failed ownerless activates do not allocate a pool"),
		Pool->GetAllocatedPoolSize(),
		0);
	TestEqual(
		TEXT("Failed ownerless activates do not advance activation count"),
		Pool->GetActivationCount(),
		0);

	Pool->DeactivateAllEffects();
	TestEqual(
		TEXT("DeactivateAllEffects on an empty ownerless pool stays a no-op"),
		Pool->GetAllocatedPoolSize(),
		0);
	TestEqual(
		TEXT("DeactivateAllEffects does not invent activations"),
		Pool->GetActivationCount(),
		0);
	return true;
}

#endif
