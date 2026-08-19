#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgHud.h"
#include "SkyguardDrone.h"
#include "SkyguardGuidedLockRules.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardThreatTypes.h"
#include "Camera/CameraComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/EngineTypes.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedMissileLockRulesAreReadableEscalationTest,
	"Skyguard52.Apache.GuidedMissile.LockRulesAreSearchDetectTrackLockFire",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedMissileLockRulesAreReadableEscalationTest::RunTest(
	const FString& Parameters)
{
	TestEqual(
		TEXT("no candidate stays in search"),
		FSkyguardGuidedLockRules::PhaseFromProgress(0.9f, false),
		ESkyguardGuidedLockPhase::Search);
	TestEqual(
		TEXT("fresh contact is detect"),
		FSkyguardGuidedLockRules::PhaseFromProgress(0.1f, true),
		ESkyguardGuidedLockPhase::Detect);
	TestEqual(
		TEXT("building solution is track"),
		FSkyguardGuidedLockRules::PhaseFromProgress(0.5f, true),
		ESkyguardGuidedLockPhase::Track);
	TestEqual(
		TEXT("complete solution is lock"),
		FSkyguardGuidedLockRules::PhaseFromProgress(1.f, true),
		ESkyguardGuidedLockPhase::Lock);

	TestFalse(
		TEXT("search cannot fire"),
		FSkyguardGuidedLockRules::CanFire(ESkyguardGuidedLockPhase::Search));
	TestFalse(
		TEXT("detect cannot fire"),
		FSkyguardGuidedLockRules::CanFire(ESkyguardGuidedLockPhase::Detect));
	TestFalse(
		TEXT("track cannot fire"),
		FSkyguardGuidedLockRules::CanFire(ESkyguardGuidedLockPhase::Track));
	TestTrue(
		TEXT("only lock can fire"),
		FSkyguardGuidedLockRules::CanFire(ESkyguardGuidedLockPhase::Lock));

	const float HelmetEarly =
		0.25f / FSkyguardGuidedLockRules::HelmetLockSeconds;
	TestEqual(
		TEXT("a quarter-second helmet dwell is still detect"),
		FSkyguardGuidedLockRules::PhaseFromProgress(HelmetEarly, true),
		ESkyguardGuidedLockPhase::Detect);
	TestFalse(
		TEXT("early helmet dwell cannot fire"),
		FSkyguardGuidedLockRules::CanFire(
			FSkyguardGuidedLockRules::PhaseFromProgress(HelmetEarly, true)));

	TestEqual(
		TEXT("search label"),
		FString(FSkyguardGuidedLockRules::PhaseLabel(ESkyguardGuidedLockPhase::Search)),
		FString(TEXT("SRCH")));
	TestEqual(
		TEXT("lock label"),
		FString(FSkyguardGuidedLockRules::PhaseLabel(ESkyguardGuidedLockPhase::Lock)),
		FString(TEXT("LCK")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedMissileHelmetAndSensorDifferTest,
	"Skyguard52.Apache.GuidedMissile.HelmetAndSensorDiffer",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedMissileHelmetAndSensorDifferTest::RunTest(
	const FString& Parameters)
{
	TestTrue(
		TEXT("helmet lock is slower than the targeting-sensor"),
		FSkyguardGuidedLockRules::HelmetLockSeconds >
			FSkyguardGuidedLockRules::SensorLockSeconds);
	TestTrue(
		TEXT("helmet cone is wider than the targeting-sensor"),
		FSkyguardGuidedLockRules::HelmetAcquireDegrees >
			FSkyguardGuidedLockRules::SensorAcquireDegrees);
	TestTrue(
		TEXT("8 deg is a helmet contact"),
		FSkyguardGuidedLockRules::IsInsideAcquireCone(
			8.f,
			ESkyguardCpgSightMode::Helmet));
	TestFalse(
		TEXT("8 deg is outside the targeting-sensor"),
		FSkyguardGuidedLockRules::IsInsideAcquireCone(
			8.f,
			ESkyguardCpgSightMode::TargetingSensor));

	const float SensorDone = 1.f;
	const float HelmetAtSensorDone =
		FSkyguardGuidedLockRules::SensorLockSeconds /
		FSkyguardGuidedLockRules::HelmetLockSeconds;
	TestEqual(
		TEXT("sensor clock reaches lock first"),
		FSkyguardGuidedLockRules::PhaseFromProgress(SensorDone, true),
		ESkyguardGuidedLockPhase::Lock);
	TestEqual(
		TEXT("helmet is still tracking when the sensor would lock"),
		FSkyguardGuidedLockRules::PhaseFromProgress(HelmetAtSensorDone, true),
		ESkyguardGuidedLockPhase::Track);

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}
	Gunner->bApacheGunnerMode = true;
	TestEqual(
		TEXT("default CPG sight is helmet"),
		Gunner->GetCpgSightMode(),
		ESkyguardCpgSightMode::Helmet);
	TestEqual(
		TEXT("helmet uses the helmet clock"),
		Gunner->GetActiveLockSeconds(),
		FSkyguardGuidedLockRules::HelmetLockSeconds);
	TestEqual(
		TEXT("helmet uses the helmet cone"),
		Gunner->GetActiveLockAngleDegrees(),
		FSkyguardGuidedLockRules::HelmetAcquireDegrees);
	TestEqual(
		TEXT("helmet tape"),
		FString(SkyguardCpgSightLabel(Gunner->GetCpgSightMode())),
		FString(TEXT("HMD")));

	Gunner->bADS = true;
	TestEqual(
		TEXT("RMB is targeting-sensor"),
		Gunner->GetCpgSightMode(),
		ESkyguardCpgSightMode::TargetingSensor);
	TestEqual(
		TEXT("sensor uses the sensor clock"),
		Gunner->GetActiveLockSeconds(),
		FSkyguardGuidedLockRules::SensorLockSeconds);
	TestEqual(
		TEXT("sensor uses the sensor cone"),
		Gunner->GetActiveLockAngleDegrees(),
		FSkyguardGuidedLockRules::SensorAcquireDegrees);
	TestEqual(
		TEXT("sensor tape"),
		FString(SkyguardCpgSightLabel(Gunner->GetCpgSightMode())),
		FString(TEXT("SNSR")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedMissileFireRequiresLockTest,
	"Skyguard52.Apache.GuidedMissile.FireRequiresCompletedLock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedMissileFireRequiresLockTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardGuidedLockFireWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	// NewObject(World) does not register the actor, so GetWorld() stays null
	// and FireGuidedMissile returns before spawn. SpawnActor puts the CPG
	// in the world. AlwaysSpawn avoids a Character capsule blocking the pawn.
	FActorSpawnParameters GunnerSpawn;
	GunnerSpawn.SpawnCollisionHandlingOverride =
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>(
		FVector::ZeroVector,
		FRotator::ZeroRotator,
		GunnerSpawn);
	ASkyguardDrone* Armor = World->SpawnActor<ASkyguardDrone>(
		FVector(2000.f, 0.f, 0.f),
		FRotator::ZeroRotator);
	TestNotNull(TEXT("gunner"), Gunner);
	TestNotNull(TEXT("armor"), Armor);
	if (!Gunner || !Armor)
	{
		World->DestroyWorld(false);
		return false;
	}
	if (!Gunner->GunnerCamera)
	{
		UCameraComponent* Camera = NewObject<UCameraComponent>(
			Gunner,
			TEXT("AutomationCpgCamera"));
		if (USceneComponent* Root = Gunner->GetRootComponent())
		{
			Camera->SetupAttachment(Root);
		}
		Camera->RegisterComponent();
		Gunner->GunnerCamera = Camera;
	}
	TestNotNull(
		TEXT("CPG camera is live so the fire gate can run"),
		Gunner->GunnerCamera.Get());
	TestNotNull(TEXT("gunner has a world"), Gunner->GetWorld());

	Armor->ConfigureThreat(ESkyguardThreatKind::GroundArmor);
	Gunner->bApacheGunnerMode = true;
	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	Gunner->IglaTarget = Armor;
	Gunner->IglaLockProgress = 0.35f;

	const int32 AmmoBefore = Gunner->GetGuidedAmmo();
	TestEqual(
		TEXT("partial solution is track"),
		Gunner->GetGuidedLockPhase(),
		ESkyguardGuidedLockPhase::Track);
	TestFalse(TEXT("track cannot fire"), Gunner->CanFireGuidedMissile());

	Gunner->FireShot();
	TestEqual(
		TEXT("space does not dump a missile before lock"),
		Gunner->GetGuidedAmmo(),
		AmmoBefore);
	TestTrue(
		TEXT("early fire keeps the track target"),
		Gunner->GetCpgLockTarget() == static_cast<AActor*>(Armor));
	TestEqual(
		TEXT("early fire does not reset lock progress"),
		Gunner->GetGuidedLockPhase(),
		ESkyguardGuidedLockPhase::Track);

	Gunner->FireGuidedMissile();
	TestEqual(
		TEXT("direct launch is also gated"),
		Gunner->GetGuidedAmmo(),
		AmmoBefore);

	const FSkyguardCpgHudSnapshot Tracking = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("HUD names guided missiles"), Tracking.WeaponLine.Contains(TEXT("MSL")));
	TestTrue(TEXT("HUD shows track"), Tracking.WeaponLine.Contains(TEXT("TRK")));
	TestTrue(TEXT("HUD lock line shows track"), Tracking.LockLine.Contains(TEXT("TRK")));
	TestFalse(
		TEXT("tracking HUD is not Yak/Igla/rifle"),
		SkyguardCpgHudHasLegacyLiveWording(
			Tracking.WeaponLine + Tracking.LockLine + Tracking.EufdLine));

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Cannon);
	Gunner->IglaTarget = Armor;
	Gunner->IglaLockProgress = 0.95f;
	Gunner->UpdateIglaLock(0.25f);
	TestEqual(
		TEXT("cannon station does not keep a missile lock"),
		Gunner->GetGuidedLockPhase(),
		ESkyguardGuidedLockPhase::Search);
	TestFalse(
		TEXT("cannon station cannot sneak a missile"),
		Gunner->CanFireGuidedMissile());

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	Gunner->IglaTarget = Armor;
	Gunner->IglaLockProgress = 1.f;
	TestTrue(TEXT("completed lock can fire"), Gunner->CanFireGuidedMissile());
	Gunner->FireGuidedMissile();
	TestEqual(
		TEXT("lock is the fire gate"),
		Gunner->GetGuidedAmmo(),
		AmmoBefore - 1);
	TestEqual(
		TEXT("launch returns the seeker to search"),
		Gunner->GetGuidedLockPhase(),
		ESkyguardGuidedLockPhase::Search);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedMissileAcquireLockTest,
	"Skyguard52.Apache.GuidedMissile.AcquireLock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedMissileAcquireLockTest::RunTest(const FString& Parameters)
{
	float EarlyProgress = 0.f;
	bool bEarlyCandidate = true;
	const ESkyguardGuidedLockPhase Early = FSkyguardGuidedLockRules::StepLock(
		EarlyProgress,
		bEarlyCandidate,
		0.25f,
		ESkyguardCpgSightMode::Helmet,
		0.f,
		false);
	TestEqual(TEXT("quarter-second helmet dwell is detect"), Early, ESkyguardGuidedLockPhase::Detect);
	TestFalse(
		TEXT("partial helmet dwell cannot fire"),
		FSkyguardGuidedLockRules::CanFire(Early));
	TestTrue(TEXT("candidate stays while acquiring"), bEarlyCandidate);

	float HelmetProgress = 0.f;
	bool bHelmetCandidate = true;
	const ESkyguardGuidedLockPhase HelmetLock = FSkyguardGuidedLockRules::StepLock(
		HelmetProgress,
		bHelmetCandidate,
		FSkyguardGuidedLockRules::HelmetLockSeconds,
		ESkyguardCpgSightMode::Helmet,
		0.f,
		false);
	TestEqual(TEXT("helmet clock reaches lock"), HelmetLock, ESkyguardGuidedLockPhase::Lock);
	TestEqual(TEXT("helmet progress is complete"), HelmetProgress, 1.f);
	TestTrue(
		TEXT("completed helmet lock can fire"),
		FSkyguardGuidedLockRules::CanFire(HelmetLock));

	float HelmetAtSensorClock = 0.f;
	bool bHelmetAtSensor = true;
	const ESkyguardGuidedLockPhase SensorAtHelmetDone = FSkyguardGuidedLockRules::StepLock(
		HelmetAtSensorClock,
		bHelmetAtSensor,
		FSkyguardGuidedLockRules::SensorLockSeconds,
		ESkyguardCpgSightMode::Helmet,
		0.f,
		false);
	TestEqual(
		TEXT("helmet is still tracking at the sensor lock clock"),
		SensorAtHelmetDone,
		ESkyguardGuidedLockPhase::Track);

	float SensorProgress = 0.f;
	bool bSensorCandidate = true;
	const ESkyguardGuidedLockPhase SensorLock = FSkyguardGuidedLockRules::StepLock(
		SensorProgress,
		bSensorCandidate,
		FSkyguardGuidedLockRules::SensorLockSeconds,
		ESkyguardCpgSightMode::TargetingSensor,
		0.f,
		false);
	TestEqual(TEXT("sensor clock acquires lock"), SensorLock, ESkyguardGuidedLockPhase::Lock);
	TestTrue(
		TEXT("completed sensor lock can fire"),
		FSkyguardGuidedLockRules::CanFire(SensorLock));

	float WideProgress = 0.f;
	bool bWideCandidate = true;
	const ESkyguardGuidedLockPhase OutsideSensor = FSkyguardGuidedLockRules::StepLock(
		WideProgress,
		bWideCandidate,
		FSkyguardGuidedLockRules::SensorLockSeconds,
		ESkyguardCpgSightMode::TargetingSensor,
		8.f,
		false);
	TestEqual(
		TEXT("8 deg does not acquire on the targeting-sensor"),
		OutsideSensor,
		ESkyguardGuidedLockPhase::Detect);
	TestEqual(TEXT("out-of-cone progress stays at zero"), WideProgress, 0.f);
	TestFalse(
		TEXT("out-of-cone cannot fire"),
		FSkyguardGuidedLockRules::CanFire(OutsideSensor));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedMissileHoldLockTest,
	"Skyguard52.Apache.GuidedMissile.HoldLock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedMissileHoldLockTest::RunTest(const FString& Parameters)
{
	float Progress = 0.f;
	bool bHasCandidate = true;
	const ESkyguardGuidedLockPhase Acquired = FSkyguardGuidedLockRules::StepLock(
		Progress,
		bHasCandidate,
		FSkyguardGuidedLockRules::HelmetLockSeconds,
		ESkyguardCpgSightMode::Helmet,
		4.f,
		false);
	TestEqual(TEXT("hold starts from a completed lock"), Acquired, ESkyguardGuidedLockPhase::Lock);

	const ESkyguardGuidedLockPhase Held = FSkyguardGuidedLockRules::StepLock(
		Progress,
		bHasCandidate,
		2.f,
		ESkyguardCpgSightMode::Helmet,
		4.f,
		false);
	TestEqual(TEXT("in-cone dwell holds lock"), Held, ESkyguardGuidedLockPhase::Lock);
	TestEqual(TEXT("held progress stays complete"), Progress, 1.f);
	TestTrue(TEXT("held lock still has a candidate"), bHasCandidate);
	TestTrue(
		TEXT("held lock can still fire"),
		FSkyguardGuidedLockRules::CanFire(Held));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedMissileLockBreaksOnFlareTest,
	"Skyguard52.Apache.GuidedMissile.LockBreaksOnFlare",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedMissileLockBreaksOnFlareTest::RunTest(const FString& Parameters)
{
	float Progress = 0.f;
	bool bHasCandidate = true;
	const ESkyguardGuidedLockPhase Locked = FSkyguardGuidedLockRules::StepLock(
		Progress,
		bHasCandidate,
		FSkyguardGuidedLockRules::SensorLockSeconds,
		ESkyguardCpgSightMode::TargetingSensor,
		0.f,
		false);
	TestEqual(TEXT("pre-flare solution is lock"), Locked, ESkyguardGuidedLockPhase::Lock);
	TestTrue(
		TEXT("pre-flare lock can fire"),
		FSkyguardGuidedLockRules::CanFire(Locked));

	const ESkyguardGuidedLockPhase Broken = FSkyguardGuidedLockRules::StepLock(
		Progress,
		bHasCandidate,
		0.f,
		ESkyguardCpgSightMode::TargetingSensor,
		0.f,
		true);
	TestEqual(TEXT("PopFlares dumps lock to search"), Broken, ESkyguardGuidedLockPhase::Search);
	TestEqual(TEXT("flare zeros progress"), Progress, 0.f);
	TestFalse(TEXT("flare drops the candidate"), bHasCandidate);
	TestFalse(
		TEXT("broken lock cannot fire"),
		FSkyguardGuidedLockRules::CanFire(Broken));
	TestEqual(
		TEXT("flare dump stays on CPG search tape"),
		FString(FSkyguardGuidedLockRules::PhaseLabel(Broken)),
		FString(TEXT("SRCH")));
	TestFalse(
		TEXT("flare dump tape is not Yak/Igla/rifle"),
		SkyguardCpgHudHasLegacyLiveWording(
			FString(FSkyguardGuidedLockRules::PhaseLabel(Broken)) +
			FString(FSkyguardGuidedLockRules::SightLabel(
				ESkyguardCpgSightMode::TargetingSensor))));

	Progress = 0.5f;
	bHasCandidate = true;
	const ESkyguardGuidedLockPhase TrackBroken = FSkyguardGuidedLockRules::StepLock(
		Progress,
		bHasCandidate,
		0.16f,
		ESkyguardCpgSightMode::Helmet,
		0.f,
		true);
	TestEqual(TEXT("flare also dumps a track solution"), TrackBroken, ESkyguardGuidedLockPhase::Search);
	TestFalse(TEXT("track flare cannot fire"), FSkyguardGuidedLockRules::CanFire(TrackBroken));
	return true;
}

#endif
