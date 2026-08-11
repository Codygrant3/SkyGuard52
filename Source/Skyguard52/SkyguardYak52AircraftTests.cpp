#include "Misc/AutomationTest.h"

#include "SkyguardYak52Aircraft.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardYak52AircraftRuntimeContractTest,
	"Skyguard52.Aircraft.Yak52.RuntimeContract",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardYak52AircraftRuntimeContractTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(EWorldType::Game, false, TEXT("SkyguardYak52AutomationWorld"));
	TestNotNull(TEXT("Automation world is created"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardYak52Aircraft* Aircraft = World->SpawnActor<ASkyguardYak52Aircraft>();
	TestNotNull(TEXT("Yak-52 runtime parent spawns"), Aircraft);
	if (Aircraft)
	{
		TestNotNull(TEXT("Rear gunner mount exists"), Aircraft->GetRearGunnerMount());
		TestNotNull(TEXT("Rear eye mount exists"), Aircraft->GetRearEyeMount());
		TestNotNull(TEXT("Rear weapon mount exists"), Aircraft->GetRearWeaponMount());

		TestTrue(
			TEXT("Rear eye uses the governed L88 marker height"),
			FMath::IsNearlyEqual(
				Aircraft->GetRearEyeMount()->GetRelativeLocation().Z,
				102.f,
				0.01f));

		Aircraft->SetEnginePower(1.f);
		Aircraft->Tick(1.f);
		TestTrue(TEXT("Propeller remains at a flight RPM"), Aircraft->GetPropellerRPM() >= 1800.f);

		Aircraft->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
		Aircraft->Tick(1.f);
		TestEqual(
			TEXT("Latest pilot command is retained"),
			Aircraft->GetPilotCommand(),
			ESkyguardPilotCommand::OrbitLeft);

		TestTrue(
			TEXT("Undamaged aircraft reports zero damage fraction"),
			FMath::IsNearlyZero(Aircraft->GetDamageFraction()));
		Aircraft->ApplyDamage(Aircraft->MaxIntegrity * 0.25f);
		TestTrue(
			TEXT("Partial damage reports expected fraction"),
			FMath::IsNearlyEqual(Aircraft->GetDamageFraction(), 0.25f, 0.01f));
		Aircraft->ApplyDamage(Aircraft->MaxIntegrity);
		TestTrue(
			TEXT("Overkill clamps integrity at zero"),
			FMath::IsNearlyZero(Aircraft->CurrentIntegrity));
		TestTrue(
			TEXT("Depleted aircraft reports full damage fraction"),
			FMath::IsNearlyEqual(Aircraft->GetDamageFraction(), 1.f, 0.01f));
	}

	World->DestroyWorld(false);
	return true;
}

#endif
