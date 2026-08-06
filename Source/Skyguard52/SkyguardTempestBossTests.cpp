#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardTempestBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardTempestBossTests
{
	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardTempestBossTestWorld"));
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
		ASkyguardTempestBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardTempestSequenceTest,
	"Skyguard52.Mission05.Tempest.LightningTurbulenceIglaAndBoundedDestruction",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardTempestSequenceTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardTempestBossTests;
	FWorldScope Scope;
	ASkyguardTempestBoss* Boss =
		Scope.Get()->SpawnActor<ASkyguardTempestBoss>();
	TestNotNull(TEXT("Tempest spawns"), Boss);
	if (!Boss)
	{
		return false;
	}
	Scope.Get()->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}
	TestEqual(TEXT("Four weak points register"), Boss->WeakPoints.Num(), 4);
	TestEqual(TEXT("Three debris pieces register"), Boss->GetDefeatDebrisPieceCount(), 3);
	TestFalse(TEXT("Boom is hidden before lightning"), Rifle(Boss, Boss->PortDischargeBoom));
	Boss->SetLightningExposed(true);
	TestTrue(TEXT("Lightning reveals port boom"), Rifle(Boss, Boss->PortDischargeBoom));
	TestTrue(TEXT("Lightning reveals starboard boom"), Rifle(Boss, Boss->StarboardDischargeBoom));
	TestFalse(TEXT("Weak gust does not expose servo"), Boss->ApplyCorrectiveBankGust(0.5f));
	TestTrue(TEXT("Strong gust forces corrective bank"), Boss->ApplyCorrectiveBankGust(0.85f));
	TestTrue(TEXT("Corrective bank exposes servo"), Rifle(Boss, Boss->ControlServo));
	TestFalse(TEXT("Igla remains gated before stabilization"), Boss->IsIglaLockEligible());
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Extend);
	TestTrue(TEXT("Extend stabilizes lock through turbulence"), Boss->AdvanceStabilizedIglaLock(8.f, 0.85f));
	TestTrue(TEXT("Stabilized lock enables Igla"), Boss->IsIglaLockEligible());
	TestTrue(
		TEXT("Igla destroys intake"),
		Boss->ApplyIglaStrike(
			Boss->EngineIntake->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	TestEqual(TEXT("Tempest is defeated"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	TestEqual(TEXT("All governed points destroyed"), Boss->GetTelemetry().WeakPointsDestroyed, 4);
	return true;
}

#endif
