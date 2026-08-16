#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardApacheAircraft.h"
#include "SkyguardBossTypes.h"
#include "SkyguardPilotVoice.h"
#include "SkyguardPlayerAircraft.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/World.h"
#include "GameFramework/InputSettings.h"
#include "Misc/AutomationTest.h"

namespace
{
	bool LineHasBannedTerm(const FString& Text)
	{
		const FString Lower = Text.ToLower();
		return Lower.Contains(TEXT("igla")) ||
			Lower.Contains(TEXT("yak")) ||
			Lower.Contains(TEXT("rifle"));
	}

	bool HasPilotAction(const FName Name)
	{
		const UInputSettings* Settings = GetDefault<UInputSettings>();
		if (!Settings)
		{
			return false;
		}
		TArray<FInputActionKeyMapping> Mappings;
		Settings->GetActionMappingByName(Name, Mappings);
		return Mappings.Num() > 0;
	}
}

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

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApachePilotCommandChangesAndConfirmsTest,
	"Skyguard52.Apache.PilotCommandChangesAndConfirms",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApachePilotCommandChangesAndConfirmsTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApachePilotConfirmWorld"));
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

	const int32 ConfirmsBefore = Apache->GetPilotConfirmationsIssued();
	Apache->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestEqual(
		TEXT("IssuePilotCommand changes GetPilotCommand"),
		Apache->GetPilotCommand(),
		ESkyguardPilotCommand::OrbitLeft);
	TestEqual(
		TEXT("ConfirmCommand fires on a new command"),
		Apache->GetPilotConfirmationsIssued(),
		ConfirmsBefore + 1);

	Apache->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestEqual(
		TEXT("repeat command does not re-confirm"),
		Apache->GetPilotConfirmationsIssued(),
		ConfirmsBefore + 1);

	Apache->IssuePilotCommand(ESkyguardPilotCommand::Break);
	TestEqual(
		TEXT("break is retained"),
		Apache->GetPilotCommand(),
		ESkyguardPilotCommand::Break);
	TestEqual(
		TEXT("ConfirmCommand fires again on a different command"),
		Apache->GetPilotConfirmationsIssued(),
		ConfirmsBefore + 2);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheOrbitHoldBreakMotionDifferTest,
	"Skyguard52.Apache.OrbitHoldBreakMotionDiffer",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheOrbitHoldBreakMotionDifferTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApachePilotMotionWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	auto SpawnGunship = [World]() -> ASkyguardApacheAircraft*
	{
		ASkyguardApacheAircraft* Apache =
			World->SpawnActor<ASkyguardApacheAircraft>(
				FVector(0.f, 0.f, 800.f),
				FRotator::ZeroRotator);
		if (Apache)
		{
			Apache->DispatchBeginPlay();
			Apache->SetOrbitFocus(FVector(2200.f, 0.f, 800.f));
		}
		return Apache;
	};

	auto MeasureXY = [](ASkyguardApacheAircraft* Apache,
		const ESkyguardPilotCommand Command) -> float
	{
		Apache->IssuePilotCommand(Command);
		const FVector Start = Apache->GetActorLocation();
		// Zero stick must not steal the AI pilot geometry.
		Apache->SetDirectFlightInput(0.f, 0.f, 0.f, 0.f);
		for (int32 Step = 0; Step < 8; ++Step)
		{
			Apache->Tick(0.2f);
		}
		return FVector::Dist2D(Start, Apache->GetActorLocation());
	};

	ASkyguardApacheAircraft* HoldShip = SpawnGunship();
	ASkyguardApacheAircraft* OrbitShip = SpawnGunship();
	ASkyguardApacheAircraft* BreakShip = SpawnGunship();
	TestNotNull(TEXT("hold ship"), HoldShip);
	TestNotNull(TEXT("orbit ship"), OrbitShip);
	TestNotNull(TEXT("break ship"), BreakShip);
	if (!HoldShip || !OrbitShip || !BreakShip)
	{
		World->DestroyWorld(false);
		return false;
	}

	const float HoldXY = MeasureXY(HoldShip, ESkyguardPilotCommand::Hold);
	const float OrbitXY = MeasureXY(OrbitShip, ESkyguardPilotCommand::OrbitLeft);
	const float BreakXY = MeasureXY(BreakShip, ESkyguardPilotCommand::Break);

	TestTrue(TEXT("hold stays nearly stationary in XY"), HoldXY < 40.f);
	TestTrue(TEXT("orbit is not the same motion as hold"), OrbitXY > HoldXY + 80.f);
	TestTrue(TEXT("break is not the same motion as hold"), BreakXY > HoldXY + 80.f);
	TestTrue(
		TEXT("orbit and break are distinct distances"),
		FMath::Abs(OrbitXY - BreakXY) > 20.f);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApachePilotConfirmCopyBansLegacyTermsTest,
	"Skyguard52.Apache.PilotConfirmCopyBansLegacyTerms",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApachePilotConfirmCopyBansLegacyTermsTest::RunTest(
	const FString& Parameters)
{
	const ESkyguardPilotCommand Commands[] = {
		ESkyguardPilotCommand::Pursuit,
		ESkyguardPilotCommand::Break,
		ESkyguardPilotCommand::OrbitLeft,
		ESkyguardPilotCommand::OrbitRight,
		ESkyguardPilotCommand::Extend,
		ESkyguardPilotCommand::Hold,
		ESkyguardPilotCommand::Climb,
		ESkyguardPilotCommand::Descend,
		ESkyguardPilotCommand::AttackRun,
		ESkyguardPilotCommand::FaceTarget,
	};
	for (const ESkyguardPilotCommand Command : Commands)
	{
		const FString Line = SkyguardPilotVoice::ConfirmLineForCommand(Command);
		TestFalse(
			TEXT("pilot confirm bans Igla/Yak/rifle"),
			LineHasBannedTerm(Line));
		TestTrue(TEXT("confirm line is non-empty"), !Line.IsEmpty());
	}

	TestTrue(TEXT("PilotOrbitLeft is mapped"), HasPilotAction(TEXT("PilotOrbitLeft")));
	TestTrue(TEXT("PilotOrbitRight is mapped"), HasPilotAction(TEXT("PilotOrbitRight")));
	TestTrue(TEXT("PilotHold is mapped"), HasPilotAction(TEXT("PilotHold")));
	TestTrue(TEXT("PilotBreak is mapped"), HasPilotAction(TEXT("PilotBreak")));
	TestTrue(TEXT("PilotAttackRun is mapped"), HasPilotAction(TEXT("PilotAttackRun")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheSensorHitDoesNotDamageEnginesTest,
	"Skyguard52.Apache.SensorHitDoesNotDamageEngines",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheSensorHitDoesNotDamageEnginesTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheSensorVsEngineWorld"));
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
	TestFalse(TEXT("engines start up"), Apache->AreEnginesDown());
	TestTrue(
		TEXT("hull starts intact"),
		FMath::IsNearlyZero(Apache->GetDamageFraction()));

	Apache->ApplySystemHit(ESkyguardApacheSystem::Sensor, 999.f);
	TestFalse(TEXT("TADS is dead"), Apache->IsSensorLive());
	TestFalse(
		TEXT("killing TADS does not kill engines"),
		Apache->AreEnginesDown());
	TestTrue(
		TEXT("killing TADS is not hull damage"),
		FMath::IsNearlyZero(Apache->GetDamageFraction()));

	Apache->ApplySystemHit(ESkyguardApacheSystem::Engines, 999.f);
	TestTrue(TEXT("engines can die on their own"), Apache->AreEnginesDown());
	TestFalse(TEXT("TADS stays dead"), Apache->IsSensorLive());
	TestTrue(
		TEXT("engine hit is not a second hull bar"),
		FMath::IsNearlyZero(Apache->GetDamageFraction()));

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheCanopyGlassFlagIsIndependentTest,
	"Skyguard52.Apache.CanopyGlassFlagIsIndependent",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheCanopyGlassFlagIsIndependentTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheGlassWorld"));
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

	TestFalse(TEXT("glass starts clear"), Apache->IsCanopyGlassCracked());
	Apache->ApplySystemHit(ESkyguardApacheSystem::Canopy, 8.f);
	TestTrue(TEXT("canopy hit cracks glass"), Apache->IsCanopyGlassCracked());
	TestTrue(TEXT("glass does not kill TADS"), Apache->IsSensorLive());
	TestFalse(TEXT("glass does not kill engines"), Apache->AreEnginesDown());
	TestFalse(TEXT("glass does not jam the chin gun"), Apache->IsChinTurretDown());
	TestFalse(TEXT("glass does not kill the rotor"), Apache->IsRotorDown());
	TestTrue(
		TEXT("glass is not hull integrity"),
		FMath::IsNearlyZero(Apache->GetDamageFraction()));

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheHullApplyDamageStillWorksTest,
	"Skyguard52.Apache.HullApplyDamageStillWorks",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheHullApplyDamageStillWorksTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheHullWorld"));
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
		TEXT("starts undamaged"),
		FMath::IsNearlyZero(Apache->GetDamageFraction()));
	Apache->ApplyDamage(Apache->MaxIntegrity * 0.25f);
	TestTrue(
		TEXT("hull fraction moves"),
		FMath::IsNearlyEqual(Apache->GetDamageFraction(), 0.25f, 0.01f));
	TestTrue(TEXT("hull hit leaves TADS live"), Apache->IsSensorLive());
	TestFalse(TEXT("hull hit leaves engines up"), Apache->AreEnginesDown());
	TestFalse(TEXT("hull hit does not crack glass"), Apache->IsCanopyGlassCracked());
	TestFalse(TEXT("hull hit leaves chin up"), Apache->IsChinTurretDown());
	TestFalse(TEXT("hull hit leaves rotor up"), Apache->IsRotorDown());

	Apache->ApplyDamage(Apache->MaxIntegrity);
	TestTrue(
		TEXT("hull can still be destroyed"),
		FMath::IsNearlyEqual(Apache->GetDamageFraction(), 1.f, 0.01f));
	TestTrue(
		TEXT("hull kill is not a TADS kill"),
		Apache->IsSensorLive());
	TestFalse(
		TEXT("hull kill is not an engine kill"),
		Apache->AreEnginesDown());

	if (Apache->HullCollider)
	{
		const float Before = Apache->GetDamageFraction();
		Apache->ApplyHit(Apache->HullCollider, 10.f);
		TestTrue(
			TEXT("hull collider hit is still hull"),
			Apache->GetDamageFraction() >= Before);
		TestTrue(TEXT("hull collider hit leaves TADS live"), Apache->IsSensorLive());
	}

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheSystemKillChangesMatchingGetterTest,
	"Skyguard52.Apache.SystemKillChangesMatchingGetter",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheSystemKillChangesMatchingGetterTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApacheSystemKillWorld"));
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

	TestFalse(
		TEXT("TADS starts up"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Sensor));
	TestFalse(
		TEXT("canopy starts up"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Canopy));
	TestFalse(
		TEXT("engines start up"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Engines));
	TestFalse(
		TEXT("chin starts up"),
		Apache->IsSystemDown(ESkyguardApacheSystem::ChinTurret));
	TestFalse(
		TEXT("rotor starts up"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Rotor));

	Apache->ApplySystemHit(ESkyguardApacheSystem::Sensor, 999.f);
	TestTrue(
		TEXT("dead TADS flips sensor getter"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Sensor));
	TestFalse(TEXT("IsSensorLive dies with TADS"), Apache->IsSensorLive());
	TestFalse(
		TEXT("TADS kill does not flip engines"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Engines));

	Apache->ApplySystemHit(ESkyguardApacheSystem::Canopy, 999.f);
	TestTrue(
		TEXT("canopy kill flips glass"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Canopy));
	TestTrue(TEXT("HUD glass flag is set"), Apache->IsCanopyGlassCracked());

	Apache->ApplySystemHit(ESkyguardApacheSystem::Engines, 999.f);
	TestTrue(
		TEXT("engine kill flips engines"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Engines));
	TestTrue(TEXT("AreEnginesDown matches"), Apache->AreEnginesDown());

	Apache->ApplySystemHit(ESkyguardApacheSystem::ChinTurret, 999.f);
	TestTrue(
		TEXT("chin kill flips chin"),
		Apache->IsSystemDown(ESkyguardApacheSystem::ChinTurret));
	TestTrue(TEXT("IsChinTurretDown matches"), Apache->IsChinTurretDown());

	Apache->ApplySystemHit(ESkyguardApacheSystem::Rotor, 999.f);
	TestTrue(
		TEXT("rotor kill flips rotor"),
		Apache->IsSystemDown(ESkyguardApacheSystem::Rotor));
	TestTrue(TEXT("IsRotorDown matches"), Apache->IsRotorDown());
	TestTrue(
		TEXT("dead rotor still has limp power"),
		Apache->GetRotorPowerScale() > 0.2f);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardApacheComponentHitsChangePlayTest,
	"Skyguard52.Apache.ComponentHitsChangePlay",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardApacheComponentHitsChangePlayTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardApachePlayWorld"));
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

	Apache->SetSensorView(true);
	TestTrue(TEXT("sensor view engages"), Apache->IsSensorViewActive());
	TestTrue(TEXT("thermal starts available"), Apache->IsThermalAvailable());

	int32 Guard = 0;
	while (Apache->IsThermalAvailable() && Apache->IsSensorLive() && Guard < 40)
	{
		Apache->ApplySystemHit(ESkyguardApacheSystem::Sensor, 5.f);
		++Guard;
	}
	TestTrue(
		TEXT("thermal can die while TADS is still live"),
		Apache->IsSensorLive());
	TestFalse(TEXT("degraded TADS kills thermal"), Apache->IsThermalAvailable());
	TestTrue(
		TEXT("sensor quality dropped"),
		Apache->GetSensorQuality() < 1.f);

	Apache->ApplySystemHit(ESkyguardApacheSystem::Sensor, 999.f);
	TestFalse(TEXT("dead TADS is not live"), Apache->IsSensorLive());
	TestFalse(TEXT("dead TADS drops sensor view"), Apache->IsSensorViewActive());
	Apache->SetSensorView(true);
	TestFalse(
		TEXT("dead TADS refuses sensor view"),
		Apache->IsSensorViewActive());

	Apache->SetDirectFlightInput(1.f, 0.f, 0.f, 0.f);
	Apache->Tick(1.f);
	const float Fast = Apache->GetForwardSpeed();
	TestTrue(TEXT("healthy gunship can push speed"), Fast > 900.f);
	Apache->ApplySystemHit(ESkyguardApacheSystem::Engines, 999.f);
	TestTrue(TEXT("engines are down"), Apache->AreEnginesDown());
	TestTrue(
		TEXT("engine kill cuts forward speed"),
		Apache->GetForwardSpeed() < Fast);
	TestTrue(
		TEXT("engine limp is not a crash"),
		Apache->GetEnginePowerScale() > 0.2f);

	TestNotNull(TEXT("chin turret"), Apache->GetChinTurret());
	if (Apache->GetChinTurret())
	{
		Apache->AimChinTurret(FRotator(0.f, 80.f, 0.f));
		const float HealthyYaw =
			FMath::Abs(Apache->GetChinTurret()->GetRelativeRotation().Yaw);
		TestTrue(TEXT("healthy chin slews wide"), HealthyYaw > 70.f);
		Apache->ApplySystemHit(ESkyguardApacheSystem::ChinTurret, 999.f);
		TestTrue(TEXT("chin is down"), Apache->IsChinTurretDown());
		const float FrozenYaw = Apache->GetChinTurret()->GetRelativeRotation().Yaw;
		Apache->AimChinTurret(FRotator(0.f, -80.f, 0.f));
		TestTrue(
			TEXT("dead chin refuses slew"),
			FMath::IsNearlyEqual(
				Apache->GetChinTurret()->GetRelativeRotation().Yaw,
				FrozenYaw,
				0.1f));
		TestTrue(
			TEXT("dead chin fire scale is a penalty"),
			Apache->GetChinFireScale() < 0.15f);
	}

	Apache->ApplySystemHit(ESkyguardApacheSystem::Rotor, 999.f);
	TestTrue(TEXT("rotor is down"), Apache->IsRotorDown());
	TestTrue(
		TEXT("rotor kill is power loss not an insta-kill"),
		Apache->GetRotorPowerScale() > 0.2f);
	Apache->SetRotorPower(1.f);
	Apache->Tick(0.35f);
	TestTrue(
		TEXT("limp rotor still turns"),
		Apache->GetRotorRPM() > 100.f);

	World->DestroyWorld(false);
	return true;
}

#endif
