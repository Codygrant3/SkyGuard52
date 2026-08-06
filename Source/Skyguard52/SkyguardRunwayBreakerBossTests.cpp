#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardRunwayBreakerBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardRunwayBreakerBossTests
{
	class FScopedWorld
	{
	public:
		FScopedWorld()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardRunwayBreakerTestWorld"));
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
		ASkyguardRunwayBreakerBoss* Boss,
		USkyguardBossWeakPointComponent* Point)
	{
		return Boss->ApplyWeaponHit(
			Point, ESkyguardBossWeapon::Rifle,
			Point->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRunwayBreakerSequenceTest,
	"Skyguard52.Mission06.PayloadCarrier.SequenceIglaAndBoundedDestruction",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRunwayBreakerSequenceTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRunwayBreakerBossTests;
	FScopedWorld TestWorld;
	ASkyguardRunwayBreakerBoss* Boss =
		TestWorld.Get()->SpawnActor<ASkyguardRunwayBreakerBoss>();
	TestNotNull(TEXT("Runway Breaker spawns"), Boss);
	if (!Boss)
	{
		return false;
	}
	TestWorld.Get()->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}

	TestEqual(TEXT("Four governed points register"), Boss->WeakPoints.Num(), 4);
	TestTrue(TEXT("Runway rack starts exposed"), Boss->RunwayRack->bExposed);
	TestTrue(TEXT("Hangar rack starts exposed"), Boss->HangarRack->bExposed);
	TestFalse(TEXT("Heat manifold starts protected"), Boss->HeatManifold->bExposed);
	TestFalse(TEXT("Engine starts protected"), Boss->PortEngine->bExposed);
	TestTrue(TEXT("Rifle jams runway rack"), Rifle(Boss, Boss->RunwayRack));
	TestFalse(TEXT("One rack does not expose manifold"), Boss->HeatManifold->bExposed);
	TestTrue(TEXT("Rifle jams hangar rack"), Rifle(Boss, Boss->HangarRack));
	TestTrue(TEXT("Both racks expose manifold"), Boss->HeatManifold->bExposed);
	TestTrue(TEXT("Rifle destroys heat manifold"), Rifle(Boss, Boss->HeatManifold));
	TestTrue(TEXT("Manifold loss opens Igla lock"), Boss->IsIglaLockEligible());
	TestTrue(
		TEXT("Igla destroys port engine"),
		Boss->ApplyIglaStrike(
			Boss->PortEngine->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	TestEqual(TEXT("Engine loss defeats carrier"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	TestEqual(TEXT("Four physical weak points destroyed"), Boss->GetTelemetry().WeakPointsDestroyed, 4);
	TestEqual(TEXT("Exactly three breakup pieces exist"), Boss->GetDefeatDebrisPieceCount(), 3);
	TestTrue(TEXT("Port wing debris activates"), Boss->DebrisPortWing->IsVisible());
	TestTrue(TEXT("Payload bay debris activates"), Boss->DebrisPayloadBay->IsVisible());
	TestTrue(TEXT("Engine debris activates"), Boss->DebrisEngine->IsVisible());
	return true;
}

#endif
