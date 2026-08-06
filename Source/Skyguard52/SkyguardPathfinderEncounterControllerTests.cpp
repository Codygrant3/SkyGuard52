#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardPathfinderEncounterController.h"
#include "SkyguardPathfinderBoss.h"
#include "SkyguardBossWeakPointComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardPathfinderEncounterControllerTests
{
	class FScopedEncounterWorld
	{
	public:
		FScopedEncounterWorld()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game,
				false,
				TEXT("SkyguardPathfinderEncounterAutomationWorld"));
			check(World);

			FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}

		~FScopedEncounterWorld()
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

	void AdvanceFor(
		USkyguardPathfinderEncounterController* Controller,
		const float Duration,
		const float Step = 0.05f)
	{
		float Remaining = Duration;
		while (Remaining > UE_KINDA_SMALL_NUMBER)
		{
			const float ThisStep = FMath::Min(Step, Remaining);
			Controller->AdvanceEncounter(ThisStep);
			Remaining -= ThisStep;
		}
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPathfinderEncounterControllerTest,
	"Skyguard52.Boss.Pathfinder.EncounterFlightAndAttackController",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPathfinderEncounterControllerTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardPathfinderEncounterControllerTests;

	FScopedEncounterWorld TestWorld;
	const FVector RouteStart(1000.f, -500.f, 600.f);
	const FRotator RouteRotation(0.f, 27.f, 0.f);
	ASkyguardPathfinderBoss* Boss =
		TestWorld.Get()->SpawnActor<ASkyguardPathfinderBoss>(
			ASkyguardPathfinderBoss::StaticClass(),
			RouteStart,
			RouteRotation);
	TestNotNull(TEXT("Pathfinder boss spawns for encounter test"), Boss);
	if (!Boss)
	{
		return false;
	}
	TestWorld.Get()->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}

	USkyguardPathfinderEncounterController* Controller = Boss->EncounterController;
	TestNotNull(TEXT("Pathfinder owns a deterministic encounter controller"), Controller);
	if (!Controller)
	{
		return false;
	}
	Controller->bAutoAdvance = false;
	const FTransform RouteOrigin(RouteRotation, RouteStart);

	Boss->IssuePilotCommand(ESkyguardPilotCommand::Pursuit);
	Controller->ResetEncounterState(RouteOrigin);
	AdvanceFor(Controller, 1.f);
	const float PursuitProgress = Controller->GetRouteProgress();
	const FVector PursuitLocal = RouteOrigin.InverseTransformPosition(Boss->GetActorLocation());
	TestTrue(TEXT("Approach advances along the coastal ingress route"), PursuitProgress > 0.f);
	TestTrue(TEXT("Approach remains in its low-water altitude band"), FMath::Abs(PursuitLocal.Z) < 5.f);
	TestTrue(TEXT("Approach route state is safe"), Controller->IsRouteStateSafe());

	Boss->IssuePilotCommand(ESkyguardPilotCommand::Extend);
	Controller->ResetEncounterState(RouteOrigin);
	AdvanceFor(Controller, 1.f);
	const float ExtendProgress = Controller->GetRouteProgress();
	TestTrue(TEXT("Extend gives the boss more objective progress than Pursuit"), ExtendProgress > PursuitProgress);

	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	Controller->ResetEncounterState(RouteOrigin);
	AdvanceFor(Controller, 0.5f);
	const float OrbitLeftY =
		RouteOrigin.InverseTransformPosition(Boss->GetActorLocation()).Y;
	TestTrue(TEXT("Orbit Left creates a left-side firing presentation"), OrbitLeftY < -100.f);
	TestTrue(TEXT("Orbit Left remains inside the route corridor"), Controller->IsRouteStateSafe());

	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	Controller->ResetEncounterState(RouteOrigin);
	AdvanceFor(Controller, 0.5f);
	const float OrbitRightY =
		RouteOrigin.InverseTransformPosition(Boss->GetActorLocation()).Y;
	TestTrue(TEXT("Orbit Right creates a right-side firing presentation"), OrbitRightY > 100.f);
	TestTrue(TEXT("Orbit commands produce opposite lateral effects"), OrbitRightY > OrbitLeftY);

	Boss->IssuePilotCommand(ESkyguardPilotCommand::Break);
	Controller->ResetEncounterState(RouteOrigin);
	AdvanceFor(Controller, 0.5f);
	const FVector BreakLocal =
		RouteOrigin.InverseTransformPosition(Boss->GetActorLocation());
	TestTrue(TEXT("Break adds a bounded evasive climb"), BreakLocal.Z > 100.f);
	TestTrue(TEXT("Break remains inside the route corridor"), Controller->IsRouteStateSafe());

	Boss->IssuePilotCommand(ESkyguardPilotCommand::Pursuit);
	Controller->ResetEncounterState(RouteOrigin);
	Controller->ApproachAttackIntervalSeconds = 0.5f;
	Controller->AttackTelegraphLeadSeconds = 0.2f;
	Controller->MaxTelegraphsPerEncounter = 2;
	AdvanceFor(Controller, 2.f);
	TestEqual(TEXT("Attack telegraphs stop at their hard encounter budget"), Controller->GetTelegraphsTriggered(), 2);
	TestFalse(TEXT("No telegraph remains active after the budget is exhausted"), Controller->IsAttackTelegraphActive());
	TestTrue(TEXT("Telegraph cycling does not disturb route safety"), Controller->IsRouteStateSafe());

	Controller->RouteLengthCm = 5000.f;
	Controller->ResetEncounterState(RouteOrigin);
	AdvanceFor(Controller, 20.f);
	TestTrue(TEXT("Route progress never exceeds the protected-object boundary"), Controller->GetRouteProgress() <= 5000.f);
	TestTrue(TEXT("Long-running approach remains finite and bounded"), Controller->IsRouteStateSafe());

	Controller->RouteLengthCm = 45000.f;
	Controller->ResetEncounterState(RouteOrigin);
	TestTrue(
		TEXT("Rifle destroys Pathfinder command antenna"),
		Boss->ApplyWeaponHit(
			Boss->CommandAntenna,
			ESkyguardBossWeapon::Rifle,
			Boss->CommandAntenna->MaxIntegrity,
			RouteStart,
			FVector::ForwardVector));
	TestTrue(
		TEXT("Rifle destroys Pathfinder nose camera"),
		Boss->ApplyWeaponHit(
			Boss->NoseCamera,
			ESkyguardBossWeapon::Rifle,
			Boss->NoseCamera->MaxIntegrity,
			RouteStart,
			FVector::ForwardVector));
	AdvanceFor(Controller, 3.f);
	const FVector LockLocal =
		RouteOrigin.InverseTransformPosition(Boss->GetActorLocation());
	TestEqual(TEXT("Controller observes the lock-window phase"), Controller->ObservedPhase, ESkyguardBossPhase::LockWindow);
	TestTrue(TEXT("Disrupted Pathfinder climbs to expose its engine"), LockLocal.Z > 400.f);
	TestTrue(TEXT("Lock-window climb stays inside the altitude envelope"), Controller->IsRouteStateSafe());

	TestTrue(
		TEXT("Igla strike advances Pathfinder to critical"),
		Boss->ApplyIglaStrike(
			Boss->Engine->MaxIntegrity,
			Boss->GetActorLocation(),
			FVector::ForwardVector));
	AdvanceFor(Controller, 3.f);
	const FVector CriticalLocal =
		RouteOrigin.InverseTransformPosition(Boss->GetActorLocation());
	TestEqual(TEXT("Controller observes the critical phase"), Controller->ObservedPhase, ESkyguardBossPhase::Critical);
	TestTrue(TEXT("Damaged Pathfinder enters a broad lateral turn"), FMath::Abs(CriticalLocal.Y) > 500.f);
	TestTrue(TEXT("Critical broad turn stays inside the route envelope"), Controller->IsRouteStateSafe());

	TestTrue(
		TEXT("Rifle finish defeats Pathfinder"),
		Boss->ApplyWeaponHit(
			Boss->ControlLinkage,
			ESkyguardBossWeapon::Rifle,
			Boss->ControlLinkage->MaxIntegrity,
			Boss->GetActorLocation(),
			FVector::ForwardVector));
	Controller->AdvanceEncounter(0.05f);
	const FVector DefeatedLocation = Boss->GetActorLocation();
	AdvanceFor(Controller, 2.f);
	TestEqual(TEXT("Controller observes defeated phase"), Controller->ObservedPhase, ESkyguardBossPhase::Defeated);
	TestTrue(TEXT("Defeated controller stops authored flight movement"), Boss->GetActorLocation().Equals(DefeatedLocation, 0.01f));
	TestFalse(TEXT("Defeated controller cannot telegraph another attack"), Controller->IsAttackTelegraphActive());

	return true;
}

#endif
