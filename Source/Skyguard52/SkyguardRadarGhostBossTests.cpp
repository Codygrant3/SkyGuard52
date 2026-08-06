#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardRadarGhostBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardRadarGhostBossTests
{
	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardRadarGhostBossTestWorld"));
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
		ASkyguardRadarGhostBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadarGhostSequenceTest,
	"Skyguard52.Mission07.RadarGhost.IdentificationBilateralIglaAndBoundedDestruction",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadarGhostSequenceTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardRadarGhostBossTests;
	FWorldScope Scope;
	ASkyguardRadarGhostBoss* Boss =
		Scope.Get()->SpawnActor<ASkyguardRadarGhostBoss>();
	TestNotNull(TEXT("Radar Ghost spawns"), Boss);
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
	TestFalse(TEXT("Unidentified contact cannot expose orbit point"), Boss->OpenOrbitExposure());
	Boss->SetContactIdentified(true);
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestTrue(TEXT("Left orbit exposes modulator"), Boss->OpenOrbitExposure());
	TestTrue(TEXT("Rifle destroys signature modulator"), Rifle(Boss, Boss->SignatureModulator));
	TestFalse(TEXT("Same orbit cannot expose receiver"), Boss->OpenOrbitExposure());
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	TestTrue(TEXT("Right orbit exposes receiver"), Boss->OpenOrbitExposure());
	TestTrue(TEXT("Rifle destroys radar receiver"), Rifle(Boss, Boss->RadarReceiver));
	TestTrue(TEXT("Receiver loss exposes cooling door"), Rifle(Boss, Boss->CoolingDoor));
	TestFalse(TEXT("Igla remains gated before rear aspect"), Boss->IsIglaLockEligible());
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Pursuit);
	TestTrue(TEXT("Rear aspect opens Igla window"), Boss->OpenRearAspectIglaWindow());
	TestTrue(
		TEXT("Igla destroys engine"),
		Boss->ApplyIglaStrike(
			Boss->Engine->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	TestEqual(TEXT("Radar Ghost is defeated"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	return true;
}

#endif
