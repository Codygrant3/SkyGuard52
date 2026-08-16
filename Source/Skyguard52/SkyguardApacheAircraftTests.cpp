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

#endif
