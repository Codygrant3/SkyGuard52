#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardRoadHunterBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardRoadHunterBossTests
{
	class FScopedWorld
	{
	public:
		FScopedWorld()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false, TEXT("SkyguardRoadHunterTestWorld"));
			check(World);
			FWorldContext& Context =
				GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}
		~FScopedWorld()
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

	bool Rifle(
		ASkyguardRoadHunterBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRoadHunterSequenceTest,
	"Skyguard52.Mission03.RoadHunter.SequenceIglaAndBoundedDestruction",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRoadHunterSequenceTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRoadHunterBossTests;
	FScopedWorld TestWorld;
	ASkyguardRoadHunterBoss* Boss =
		TestWorld.Get()->SpawnActor<ASkyguardRoadHunterBoss>();
	TestNotNull(TEXT("Road Hunter spawns"), Boss);
	if (!Boss)
	{
		return false;
	}
	TestWorld.Get()->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}

	TestEqual(TEXT("Four governed weak points register"), Boss->WeakPoints.Num(), 4);
	TestTrue(TEXT("Camera begins exposed"), Boss->TargetingCamera->bExposed);
	TestFalse(TEXT("Left actuator begins protected"), Boss->LeftActuator->bExposed);
	TestFalse(TEXT("Right actuator begins protected"), Boss->RightActuator->bExposed);
	TestFalse(TEXT("Engine begins protected"), Boss->Engine->bExposed);
	TestFalse(TEXT("Igla starts unavailable"), Boss->IsIglaLockEligible());
	TestFalse(TEXT("Out-of-order actuator hit is rejected"), Rifle(Boss, Boss->LeftActuator));

	TestTrue(TEXT("Rifle blinds targeting camera"), Rifle(Boss, Boss->TargetingCamera));
	TestTrue(TEXT("Camera loss exposes left actuator"), Boss->LeftActuator->bExposed);
	TestTrue(TEXT("Camera loss exposes right actuator"), Boss->RightActuator->bExposed);
	TestTrue(TEXT("Rifle destroys left actuator"), Rifle(Boss, Boss->LeftActuator));
	TestFalse(TEXT("One actuator does not open lock"), Boss->IsIglaLockEligible());
	TestTrue(TEXT("Rifle destroys right actuator"), Rifle(Boss, Boss->RightActuator));
	TestEqual(TEXT("Both actuators open lock window"), Boss->GetBossPhase(), ESkyguardBossPhase::LockWindow);
	TestTrue(TEXT("Engine becomes Igla eligible"), Boss->IsIglaLockEligible());
	TestTrue(
		TEXT("Igla destroys engine"),
		Boss->ApplyIglaStrike(
			Boss->Engine->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	TestEqual(TEXT("Engine strike defeats Road Hunter"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	TestEqual(TEXT("Three rifle hits accepted"), Boss->GetTelemetry().RifleHits, 3);
	TestEqual(TEXT("One Igla hit accepted"), Boss->GetTelemetry().IglaHits, 1);
	TestEqual(TEXT("Four weak points destroyed"), Boss->GetTelemetry().WeakPointsDestroyed, 4);
	TestEqual(TEXT("Three breakup pieces preallocated"), Boss->GetDefeatDebrisPieceCount(), 3);
	TestTrue(TEXT("Left debris activates"), Boss->DebrisLeftWing->IsVisible());
	TestTrue(TEXT("Engine debris activates"), Boss->DebrisEngine->IsVisible());
	TestTrue(TEXT("Right debris activates"), Boss->DebrisRightWing->IsVisible());
	return true;
}

#endif
