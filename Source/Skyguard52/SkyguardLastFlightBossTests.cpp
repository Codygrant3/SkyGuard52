#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardLastFlightBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardLastFlightBossTests
{
	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardLastFlightBossTestWorld"));
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
		ASkyguardLastFlightBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardLastFlightFullVocabularyTest,
	"Skyguard52.Mission10.LastFlight.FullVocabularyAndWreckDiversion",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardLastFlightFullVocabularyTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardLastFlightBossTests;
	FWorldScope Scope;
	ASkyguardLastFlightBoss* Boss =
		Scope.Get()->SpawnActor<ASkyguardLastFlightBoss>();
	TestNotNull(TEXT("Last Flight spawns"), Boss);
	if (!Boss)
	{
		return false;
	}
	Scope.Get()->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}
	TestEqual(TEXT("Ten physical mechanisms register"), Boss->WeakPoints.Num(), 10);
	TestEqual(TEXT("Six breakup pieces register"), Boss->GetDefeatDebrisPieceCount(), 6);

	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestTrue(TEXT("Left orbit exposes port guidance"), Boss->OpenGuidanceArrayExposure());
	TestTrue(TEXT("Rifle destroys port guidance"), Rifle(Boss, Boss->PortGuidanceArray));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	TestTrue(TEXT("Right orbit exposes starboard guidance"), Boss->OpenGuidanceArrayExposure());
	TestTrue(TEXT("Rifle destroys starboard guidance"), Rifle(Boss, Boss->StarboardGuidanceArray));
	TestEqual(TEXT("Highway stage advances"), Boss->GetFinaleStage(), ESkyguardLastFlightStage::Terminal);

	TestTrue(TEXT("Terminal strike cycle opens"), Boss->BeginTerminalStrikeCycle());
	TestTrue(TEXT("Rifle destroys port bay"), Rifle(Boss, Boss->PortStrikeBayMechanism));
	TestTrue(TEXT("Rifle destroys starboard bay"), Rifle(Boss, Boss->StarboardStrikeBayMechanism));
	TestTrue(TEXT("Rifle destroys port cooling"), Rifle(Boss, Boss->PortCoolingSystem));
	TestTrue(TEXT("Rifle destroys starboard cooling"), Rifle(Boss, Boss->StarboardCoolingSystem));
	Boss->SetCivilianSeparationMeters(200.f);
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Extend);
	TestFalse(TEXT("Unsafe first lock is rejected"), Boss->OpenFirstIglaWindow());
	Boss->SetCivilianSeparationMeters(800.f);
	TestTrue(TEXT("Extend opens safe first lock"), Boss->OpenFirstIglaWindow());
	TestTrue(
		TEXT("First Igla destroys port engine"),
		Boss->ApplyIglaStrike(
			Boss->PortEngine->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));

	TestTrue(TEXT("Climb exposes jammer"), Boss->IssueClimbCommand());
	TestTrue(TEXT("Rifle destroys jammer"), Rifle(Boss, Boss->Jammer));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Extend);
	TestTrue(TEXT("Extend opens final lock"), Boss->OpenFinalIglaWindow());
	TestTrue(
		TEXT("Final Igla destroys starboard engine"),
		Boss->ApplyIglaStrike(
			Boss->StarboardEngine->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Pursuit);
	TestTrue(TEXT("Pursuit arms command-core rifle path"), Boss->ArmCommandCoreRiflePath());
	TestTrue(TEXT("Rifle disables command core"), Rifle(Boss, Boss->CommandCore));
	TestEqual(TEXT("Four finale milestones reached"), Boss->GetObjectiveMilestonesReached(), 4);
	TestEqual(TEXT("Wreck enters disabled descent"), Boss->GetFinaleStage(), ESkyguardLastFlightStage::DisabledDescent);
	TestFalse(TEXT("Disabled wreck is not yet victory"), Boss->GetBossPhase() == ESkyguardBossPhase::Defeated);
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Break);
	TestTrue(TEXT("Break diverts wreck"), Boss->DivertWreckFromCivilians());
	TestTrue(TEXT("Wreck diversion is recorded"), Boss->IsWreckDiverted());
	TestEqual(TEXT("Diversion completes defeat"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	return true;
}

#endif
