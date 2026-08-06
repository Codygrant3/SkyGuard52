#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardBreakwaterBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardBreakwaterBossTests
{
	class FScopedWorld
	{
	public:
		FScopedWorld()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false, TEXT("SkyguardBreakwaterTestWorld"));
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

	bool DestroyWithRifle(
		ASkyguardBreakwaterBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint,
			ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardBreakwaterSequenceTest,
	"Skyguard52.Mission02.Breakwater.SequenceIglaAndBoundedDestruction",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardBreakwaterSequenceTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardBreakwaterBossTests;

	FScopedWorld TestWorld;
	ASkyguardBreakwaterBoss* Boss =
		TestWorld.Get()->SpawnActor<ASkyguardBreakwaterBoss>();
	TestNotNull(TEXT("Breakwater spawns"), Boss);
	if (!Boss)
	{
		return false;
	}
	TestWorld.Get()->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}

	TestEqual(TEXT("Five physical interaction components register"), Boss->WeakPoints.Num(), 5);
	TestTrue(TEXT("Port latch starts exposed"), Boss->PortLatch->bExposed);
	TestFalse(TEXT("Starboard latch starts protected"), Boss->StarboardLatch->bExposed);
	TestFalse(TEXT("Decoys start protected"), Boss->DecoyPods->bExposed);
	TestFalse(TEXT("Engine starts protected"), Boss->Engine->bExposed);
	TestFalse(TEXT("Elevator linkage starts protected"), Boss->ElevatorLinkage->bExposed);
	TestFalse(TEXT("Igla cannot lock at approach"), Boss->IsIglaLockEligible());

	TestFalse(
		TEXT("Out-of-order rifle fire cannot damage the starboard latch"),
		DestroyWithRifle(Boss, Boss->StarboardLatch));
	TestTrue(TEXT("Rifle opens the port latch"), DestroyWithRifle(Boss, Boss->PortLatch));
	TestEqual(TEXT("Port latch enters disarm phase"), Boss->GetBossPhase(), ESkyguardBossPhase::Disarm);
	TestTrue(TEXT("Port latch exposes starboard latch"), Boss->StarboardLatch->bExposed);
	TestTrue(TEXT("Rifle opens starboard latch"), DestroyWithRifle(Boss, Boss->StarboardLatch));
	TestTrue(TEXT("Both latches expose decoy pods"), Boss->DecoyPods->bExposed);
	TestTrue(TEXT("Rifle destroys decoy pods"), DestroyWithRifle(Boss, Boss->DecoyPods));
	TestEqual(TEXT("Decoy loss opens lock window"), Boss->GetBossPhase(), ESkyguardBossPhase::LockWindow);
	TestTrue(TEXT("Engine becomes Igla eligible"), Boss->IsIglaLockEligible());

	TestTrue(
		TEXT("Igla destroys exposed engine"),
		Boss->ApplyIglaStrike(
			Boss->Engine->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	TestEqual(TEXT("Igla strike enters critical phase"), Boss->GetBossPhase(), ESkyguardBossPhase::Critical);
	TestTrue(TEXT("Engine loss exposes elevator linkage"), Boss->ElevatorLinkage->bExposed);
	TestTrue(
		TEXT("Rifle severs elevator linkage"),
		DestroyWithRifle(Boss, Boss->ElevatorLinkage));
	TestEqual(TEXT("Linkage finish defeats Breakwater"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);

	TestEqual(TEXT("Four rifle hits accepted"), Boss->GetTelemetry().RifleHits, 4);
	TestEqual(TEXT("One Igla hit accepted"), Boss->GetTelemetry().IglaHits, 1);
	TestEqual(TEXT("Five physical weak points destroyed"), Boss->GetTelemetry().WeakPointsDestroyed, 5);
	TestEqual(TEXT("Exactly three debris pieces are preallocated"), Boss->GetDefeatDebrisPieceCount(), 3);
	TestTrue(
		TEXT("Breakup remains within hard budget"),
		Boss->GetDefeatDebrisPieceCount() <= Boss->GetMaxDefeatDebrisPieces());
	TestTrue(TEXT("Port debris activates at defeat"), Boss->DebrisPortPanel->IsVisible());
	TestTrue(TEXT("Engine debris activates at defeat"), Boss->DebrisEngine->IsVisible());
	TestTrue(TEXT("Starboard debris activates at defeat"), Boss->DebrisStarboardPanel->IsVisible());
	return true;
}

#endif
