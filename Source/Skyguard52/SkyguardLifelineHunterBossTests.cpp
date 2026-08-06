#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardLifelineHunterBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardLifelineHunterBossTests
{
	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardLifelineHunterBossTestWorld"));
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
		ASkyguardLifelineHunterBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardLifelineHunterSafetyTest,
	"Skyguard52.Mission08.LifelineHunter.SensorSeparationRedirectAndBoundedDestruction",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardLifelineHunterSafetyTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardLifelineHunterBossTests;
	FWorldScope Scope;
	ASkyguardLifelineHunterBoss* Boss =
		Scope.Get()->SpawnActor<ASkyguardLifelineHunterBoss>();
	TestNotNull(TEXT("Lifeline Hunter spawns"), Boss);
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
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestTrue(TEXT("Left orbit exposes primary sensor"), Boss->OpenSensorExposure());
	TestTrue(TEXT("Rifle destroys optical tracker"), Rifle(Boss, Boss->OpticalTracker));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	TestTrue(TEXT("Right orbit exposes secondary sensor"), Boss->OpenSensorExposure());
	TestTrue(TEXT("Rifle destroys weapon servo"), Rifle(Boss, Boss->WeaponServo));
	TestTrue(TEXT("Rifle destroys countermeasure pod"), Rifle(Boss, Boss->CountermeasurePod));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Extend);
	Boss->SetFriendlySeparationMeters(200.f);
	TestFalse(TEXT("Unsafe separation blocks Igla"), Boss->OpenSafeIglaWindow());
	Boss->SetFriendlySeparationMeters(700.f);
	TestTrue(TEXT("Safe separation opens Igla"), Boss->OpenSafeIglaWindow());
	TestTrue(
		TEXT("Igla disables engine"),
		Boss->ApplyIglaStrike(
			Boss->Engine->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	TestTrue(TEXT("Boss enters disabled descent"), Boss->IsDisabledDescent());
	TestFalse(
		TEXT("Disabled descent is not yet safe defeat"),
		Boss->GetBossPhase() == ESkyguardBossPhase::Defeated);
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Break);
	TestTrue(TEXT("Break redirects disabled drone"), Boss->RedirectDisabledDrone());
	TestTrue(TEXT("Crash is redirected"), Boss->IsCrashRedirected());
	TestEqual(TEXT("Safe redirect completes defeat"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	return true;
}

#endif
