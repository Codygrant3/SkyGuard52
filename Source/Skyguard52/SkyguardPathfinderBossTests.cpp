#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardPathfinderBoss.h"
#include "SkyguardBossWeakPointComponent.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"
#include "PhysicsEngine/BodySetup.h"

namespace SkyguardPathfinderBossTests
{
	class FScopedTestWorld
	{
	public:
		FScopedTestWorld()
		{
			World = UWorld::CreateWorld(EWorldType::Game, false, TEXT("SkyguardPathfinderAutomationWorld"));
			check(World);

			FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}

		~FScopedTestWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
		}

		UWorld* Get() const { return World; }

	private:
		UWorld* World = nullptr;
	};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPathfinderBossSequenceTest,
	"Skyguard52.Boss.Pathfinder.SequenceAndBoundedDestruction",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPathfinderBossSequenceTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardPathfinderBossTests;

	FScopedTestWorld TestWorld;
	ASkyguardPathfinderBoss* Boss =
		TestWorld.Get()->SpawnActor<ASkyguardPathfinderBoss>(
			ASkyguardPathfinderBoss::StaticClass(),
			FVector::ZeroVector,
			FRotator::ZeroRotator);
	TestNotNull(TEXT("Pathfinder boss spawns"), Boss);
	if (!Boss)
	{
		return false;
	}
	TestWorld.Get()->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}

	TestEqual(TEXT("Pathfinder starts in approach"), Boss->GetBossPhase(), ESkyguardBossPhase::Approach);
	TestEqual(TEXT("Pathfinder registers four weak points at begin play"), Boss->WeakPoints.Num(), 4);
	TestFalse(TEXT("Igla cannot lock before rifle disarm"), Boss->IsIglaLockEligible());
	TestTrue(TEXT("Command antenna starts exposed"), Boss->CommandAntenna->bExposed);
	TestTrue(TEXT("Nose camera starts exposed"), Boss->NoseCamera->bExposed);
	TestFalse(TEXT("Engine starts protected"), Boss->Engine->bExposed);
	TestFalse(TEXT("Control linkage starts protected"), Boss->ControlLinkage->bExposed);

	const FVector HitLocation(100.f, 0.f, 0.f);
	const FVector HitDirection(1.f, 0.f, 0.f);
	TestFalse(
		TEXT("Rifle cannot damage protected engine"),
		Boss->ApplyWeaponHit(
			Boss->Engine,
			ESkyguardBossWeapon::Rifle,
			1000.f,
			HitLocation,
			HitDirection));
	TestEqual(TEXT("Rejected weapon is not counted as a hit"), Boss->GetTelemetry().RifleHits, 0);

	TestTrue(
		TEXT("Rifle destroys command antenna"),
		Boss->ApplyWeaponHit(
			Boss->CommandAntenna,
			ESkyguardBossWeapon::Rifle,
			Boss->CommandAntenna->MaxIntegrity,
			HitLocation,
			HitDirection));
	TestTrue(TEXT("Command antenna is destroyed"), Boss->CommandAntenna->bDestroyed);
	TestEqual(TEXT("One disarm weak point keeps approach phase"), Boss->GetBossPhase(), ESkyguardBossPhase::Approach);
	TestFalse(TEXT("One disarm weak point is insufficient for lock"), Boss->IsIglaLockEligible());

	TestTrue(
		TEXT("Rifle destroys nose camera"),
		Boss->ApplyWeaponHit(
			Boss->NoseCamera,
			ESkyguardBossWeapon::Rifle,
			Boss->NoseCamera->MaxIntegrity,
			HitLocation,
			HitDirection));
	TestTrue(TEXT("Nose camera is destroyed"), Boss->NoseCamera->bDestroyed);
	TestEqual(TEXT("Disarm completion opens lock window"), Boss->GetBossPhase(), ESkyguardBossPhase::LockWindow);
	TestTrue(TEXT("Disarm completion enables Igla lock"), Boss->IsIglaLockEligible());
	TestTrue(TEXT("Engine becomes exposed"), Boss->Engine->bExposed);

	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Break);
	TestEqual(TEXT("Latest pilot command is retained"), Boss->CurrentPilotCommand, ESkyguardPilotCommand::Break);
	TestEqual(TEXT("Pilot command hook telemetry is deterministic"), Boss->GetTelemetry().PilotCommandsIssued, 2);

	TestTrue(
		TEXT("Igla destroys the exposed engine"),
		Boss->ApplyIglaStrike(
			Boss->Engine->MaxIntegrity,
			HitLocation,
			HitDirection));
	TestTrue(TEXT("Engine is destroyed"), Boss->Engine->bDestroyed);
	TestEqual(TEXT("Engine loss advances to critical phase"), Boss->GetBossPhase(), ESkyguardBossPhase::Critical);
	TestFalse(TEXT("Igla lock closes after engine loss"), Boss->IsIglaLockEligible());
	TestTrue(TEXT("Control linkage becomes exposed"), Boss->ControlLinkage->bExposed);

	TestTrue(
		TEXT("Rifle destroys the exposed control linkage"),
		Boss->ApplyWeaponHit(
			Boss->ControlLinkage,
			ESkyguardBossWeapon::Rifle,
			Boss->ControlLinkage->MaxIntegrity,
			HitLocation,
			HitDirection));
	TestTrue(TEXT("Control linkage is destroyed"), Boss->ControlLinkage->bDestroyed);
	TestEqual(TEXT("Control linkage finish defeats Pathfinder"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	TestFalse(TEXT("Defeated boss cannot be locked"), Boss->IsIglaLockEligible());

	const FSkyguardBossTelemetry& Telemetry = Boss->GetTelemetry();
	TestEqual(TEXT("Three accepted rifle impacts are counted"), Telemetry.RifleHits, 3);
	TestEqual(TEXT("One accepted Igla impact is counted"), Telemetry.IglaHits, 1);
	TestEqual(TEXT("All four weak points are counted once"), Telemetry.WeakPointsDestroyed, 4);

	TestEqual(TEXT("Pathfinder preallocates exactly four breakup pieces"), Boss->GetDefeatDebrisPieceCount(), 4);
	TestTrue(
		TEXT("Breakup piece count stays within the hard budget"),
		Boss->GetDefeatDebrisPieceCount() <= Boss->GetMaxDefeatDebrisPieces());
	TestTrue(TEXT("Defeat activates the preallocated nose debris"), Boss->DebrisNose->IsVisible());
	TestTrue(TEXT("Defeat activates the preallocated center debris"), Boss->DebrisCenter->IsVisible());
	TestTrue(TEXT("Defeat activates the preallocated tail debris"), Boss->DebrisTail->IsVisible());
	TestTrue(TEXT("Defeat activates the preallocated spine debris"), Boss->DebrisSpine->IsVisible());
	const UStaticMesh* SpineMesh = Boss->DebrisSpine->GetStaticMesh().Get();
	TestNotNull(TEXT("Spine debris uses the imported refinement mesh"), SpineMesh);
	if (SpineMesh)
	{
		const UBodySetup* SpineBodySetup = SpineMesh->GetBodySetup();
		TestNotNull(TEXT("Spine debris has a persisted body setup"), SpineBodySetup);
		if (SpineBodySetup)
		{
			TestTrue(
				TEXT("Spine debris has at least one simple collision primitive"),
				SpineBodySetup->AggGeom.GetElementCount() > 0);
		}
	}
	TestTrue(
		TEXT("Spine debris enables query and physics collision at defeat"),
		Boss->DebrisSpine->GetCollisionEnabled() ==
			ECollisionEnabled::QueryAndPhysics);
	TestTrue(
		TEXT("Spine debris simulates physics at defeat"),
		Boss->DebrisSpine->IsSimulatingPhysics());
	TestTrue(TEXT("Defeated body is removed from collision"), Boss->BodyMesh->GetCollisionEnabled() == ECollisionEnabled::NoCollision);
	TestFalse(
		TEXT("Further rifle damage is rejected after defeat"),
		Boss->ApplyWeaponHit(
			Boss->ControlLinkage,
			ESkyguardBossWeapon::Rifle,
			1000.f,
			HitLocation,
			HitDirection));

	return true;
}

#endif
