#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardBlackKiteBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardBlackKiteBossTests
{
	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardBlackKiteBossTestWorld"));
			check(World);
			FWorldContext& Context =
				GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}
		~FWorldScope()
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
		ASkyguardBlackKiteBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardBlackKiteSequenceTest,
	"Skyguard52.Mission04.BlackKite.SearchlightJammerIglaAndBoundedDestruction",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardBlackKiteSequenceTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardBlackKiteBossTests;
	FWorldScope Scope;
	ASkyguardBlackKiteBoss* Boss =
		Scope.Get()->SpawnActor<ASkyguardBlackKiteBoss>();
	TestNotNull(TEXT("Black Kite spawns"), Boss);
	if (!Boss)
	{
		return false;
	}
	Scope.Get()->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}
	TestEqual(TEXT("Four physical weak points register"), Boss->WeakPoints.Num(), 4);
	TestEqual(TEXT("Three debris pieces register"), Boss->GetDefeatDebrisPieceCount(), 3);
	TestFalse(TEXT("Vane is hidden before searchlight"), Rifle(Boss, Boss->PortNavigationVane));
	Boss->SetSearchlightTracked(true);
	TestTrue(TEXT("Searchlight reveals port vane"), Rifle(Boss, Boss->PortNavigationVane));
	TestTrue(TEXT("Searchlight reveals starboard vane"), Rifle(Boss, Boss->StarboardNavigationVane));
	TestTrue(TEXT("Both vanes expose jammer"), Boss->Jammer->bExposed);
	TestTrue(TEXT("Rifle destroys jammer"), Rifle(Boss, Boss->Jammer));
	TestTrue(TEXT("Jammer loss enables Igla"), Boss->IsIglaLockEligible());
	TestTrue(
		TEXT("Igla destroys exposed power bus"),
		Boss->ApplyIglaStrike(
			Boss->PowerBus->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	TestEqual(TEXT("Black Kite is defeated"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	TestEqual(TEXT("All governed weak points destroyed"), Boss->GetTelemetry().WeakPointsDestroyed, 4);
	return true;
}

#endif
