#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardApacheAircraft.h"
#include "SkyguardBossTypes.h"
#include "SkyguardPlayerAircraft.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheHasFrontSeatAndChinGunTest,
	"Skyguard52.Apache.HasFrontSeatAndChinGun",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheHasFrontSeatAndChinGunTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheSeatWorld"));
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

	TestNotNull(TEXT("front gunner mount"), Apache->GetGunnerMount());
	TestNotNull(TEXT("aft pilot mount"), Apache->GetPilotMount());
	TestNotNull(TEXT("chin turret"), Apache->GetChinTurret());
	TestNotNull(TEXT("weapon mount"), Apache->GetWeaponMount());
	TestNotNull(TEXT("gunner sensor turret"), Apache->GetSensorTurret());
	TestTrue(
		TEXT("CPG sits forward of aircraft origin"),
		Apache->GetGunnerMount()->GetRelativeLocation().X > 0.f);
	TestTrue(
		TEXT("pilot sits aft of the CPG"),
		Apache->GetPilotMount()->GetRelativeLocation().X <
			Apache->GetGunnerMount()->GetRelativeLocation().X);
	TestTrue(
		TEXT("TADS sits forward of the CPG"),
		Apache->GetSensorTurret()->GetRelativeLocation().X >
			Apache->GetGunnerMount()->GetRelativeLocation().X);
	Apache->ApplyDamage(35.f);
	TestTrue(TEXT("hull takes damage"), Apache->GetDamageFraction() > 0.f);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardEnsureApacheIsIdempotentTest,
	"Skyguard52.Apache.EnsureApacheIsIdempotent",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardEnsureApacheIsIdempotentTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheEnsureWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardYak52Aircraft* Yak = World->SpawnActor<ASkyguardYak52Aircraft>(
		FVector(100.f, 200.f, 300.f),
		FRotator::ZeroRotator);
	TestNotNull(TEXT("legacy yak"), Yak);

	ASkyguardApacheAircraft* First = FSkyguardPlayerAircraft::EnsureApache(World);
	ASkyguardApacheAircraft* Second = FSkyguardPlayerAircraft::EnsureApache(World);
	TestNotNull(TEXT("apache spawned"), First);
	TestTrue(TEXT("second ensure is a no-op"), First == Second);
	if (First && Yak)
	{
		TestTrue(
			TEXT("apache inherits yak transform"),
			FVector::DistSquared(First->GetActorLocation(), Yak->GetActorLocation())
				< 1.f);
		TestTrue(TEXT("legacy yak is hidden"), Yak->IsHidden());
	}

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApachePilotCommandsAreGuidedFreedomTest,
	"Skyguard52.Apache.PilotCommandsAreGuidedFreedom",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApachePilotCommandsAreGuidedFreedomTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApachePilotWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardApacheAircraft* Apache =
		World->SpawnActor<ASkyguardApacheAircraft>(
			FVector(0.f, 0.f, 800.f),
			FRotator::ZeroRotator);
	TestNotNull(TEXT("apache"), Apache);
	if (!Apache)
	{
		World->DestroyWorld(false);
		return false;
	}
	Apache->DispatchBeginPlay();
	Apache->IssuePilotCommand(ESkyguardPilotCommand::Hold);
	TestEqual(
		TEXT("hold is accepted"),
		Apache->GetPilotCommand(),
		ESkyguardPilotCommand::Hold);
	Apache->IssuePilotCommand(ESkyguardPilotCommand::AttackRun);
	TestEqual(
		TEXT("attack run is accepted"),
		Apache->GetPilotCommand(),
		ESkyguardPilotCommand::AttackRun);
	const FVector Before = Apache->GetActorLocation();
	Apache->Tick(0.25f);
	TestTrue(
		TEXT("attack run translates the gunship"),
		FVector::DistSquared(Before, Apache->GetActorLocation()) > 1.f);

	const float AltitudeBefore = Apache->GetActorLocation().Z;
	const float YawBefore = Apache->GetActorRotation().Yaw;
	Apache->SetDirectFlightInput(1.f, 1.f, 1.f, 0.f);
	Apache->Tick(0.35f);
	TestTrue(
		TEXT("W collective climbs"),
		Apache->GetActorLocation().Z > AltitudeBefore);
	TestTrue(
		TEXT("W collective accelerates"),
		Apache->GetForwardSpeed() > 900.f);
	TestTrue(
		TEXT("D / right-stick pivot yaws the nose"),
		!FMath::IsNearlyEqual(Apache->GetActorRotation().Yaw, YawBefore, 0.2f));

	World->DestroyWorld(false);
	return true;
}

#endif
