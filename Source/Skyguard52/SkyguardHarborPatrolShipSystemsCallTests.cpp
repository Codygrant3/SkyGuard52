#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgDebrief.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardPatrolShipBoss.h"
#include "SkyguardPilotVoice.h"
#include "SkyguardRadioChatterComponent.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace
{
	struct FHarborShipSystemCall
	{
		ESkyguardPatrolShipSystem System;
		ESkyguardPilotLine Line;
		const TCHAR* Label;
	};

	const FHarborShipSystemCall GRemainingShipSystemCalls[] = {
		{ESkyguardPatrolShipSystem::Cannon, ESkyguardPilotLine::ShipCannonDown, TEXT("Cannon")},
		{ESkyguardPatrolShipSystem::Launcher, ESkyguardPilotLine::ShipLauncherDown, TEXT("Launcher")},
		{ESkyguardPatrolShipSystem::Engines, ESkyguardPilotLine::ShipEnginesDown, TEXT("Engines")},
		{ESkyguardPatrolShipSystem::DroneDeck, ESkyguardPilotLine::ShipDeckDown, TEXT("DroneDeck")}};

	USkyguardRadioChatterComponent* AttachRadio(AActor* Owner, const TCHAR* Name)
	{
		if (!Owner)
		{
			return nullptr;
		}
		USkyguardRadioChatterComponent* Radio = NewObject<USkyguardRadioChatterComponent>(
			Owner,
			USkyguardRadioChatterComponent::StaticClass(),
			Name,
			RF_Transient);
		Radio->RegisterComponent();
		Radio->InterLineGapSeconds = 0.f;
		return Radio;
	}

	bool ExpectCallEventOnRadio(
		FAutomationTestBase& Test,
		USkyguardRadioChatterComponent* Radio,
		const ESkyguardPilotLine Line,
		const TCHAR* Label)
	{
		const FSkyguardRadioLine Built = SkyguardPilotVoice::MakeRadioLine(Line);
		const bool bOk =
			Test.TestEqual(
				*FString::Printf(TEXT("%s CallEvent probe"), Label),
				SkyguardPilotVoice::GetLastCalledLine(),
				Line) &&
			Test.TestEqual(
				*FString::Printf(TEXT("%s radio line id"), Label),
				Radio->GetCurrentLineId(),
				Built.LineId) &&
			Test.TestTrue(
				*FString::Printf(TEXT("%s radio played"), Label),
				Radio->GetPlayedLineCount() >= 1) &&
			Test.TestFalse(
				*FString::Printf(TEXT("%s bans Igla/Yak/rifle"), Label),
				SkyguardCpgCopyHasBannedTerm(Built.Subtitle.ToString())) &&
			Test.TestFalse(
				*FString::Printf(TEXT("%s raw text bans Igla/Yak/rifle"), Label),
				SkyguardCpgCopyHasBannedTerm(SkyguardPilotVoice::LineTextForEvent(Line)));
		return bOk;
	}

	bool ExpectSystemCopy(FAutomationTestBase& Test, const ESkyguardPilotLine Line, const TCHAR* Label)
	{
		const FString Text = SkyguardPilotVoice::LineTextForEvent(Line);
		return Test.TestFalse(
				*FString::Printf(TEXT("%s copy stays non-empty"), Label),
				Text.IsEmpty()) &&
			Test.TestFalse(
				*FString::Printf(TEXT("%s copy bans Igla/Yak/rifle"), Label),
				SkyguardCpgCopyHasBannedTerm(Text));
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborPatrolShipSystemsMapToCallEventsTest,
	"Skyguard52.Campaign.Harbor.PatrolShipSystemsMapToCallEvents",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborPatrolShipSystemsMapToCallEventsTest::RunTest(
	const FString& Parameters)
{
	for (const FHarborShipSystemCall& Call : GRemainingShipSystemCalls)
	{
		ExpectSystemCopy(*this, Call.Line, Call.Label);
	}
	ExpectSystemCopy(*this, ESkyguardPilotLine::ShipDead, TEXT("ShipDead"));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborDirectorPatrolShipSystemsFireCallEventsTest,
	"Skyguard52.Campaign.Harbor.DirectorPatrolShipSystemsFireCallEvents",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborDirectorPatrolShipSystemsFireCallEventsTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardHarborPatrolShipSystemsWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("director"), Director);
	if (!Director)
	{
		World->DestroyWorld(false);
		return false;
	}
	Director->bAutoStart = false;
	Director->StartMissionIndex(1);
	TestEqual(
		TEXT("harbor title"),
		Director->GetMissionTitle(),
		FString(TEXT("Harbor Breaker")));

	// Harbor BeatSeconds: 120 / 240 / 360 / 480 / 600. No gunner, so inbound
	// never arms and these ticks only advance beats / spawn the patrol ship.
	// IncomingRadarLiveIntervalSeconds (40) and
	// IncomingRadarDownIntervalSeconds (80) stay at their production values.
	Director->Tick(120.f);
	Director->Tick(120.f);
	Director->Tick(120.f);
	Director->Tick(120.f);
	Director->Tick(120.f);
	TestEqual(
		TEXT("fifth gate is Climax — ship is live"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Climax);
	ASkyguardPatrolShipBoss* Ship = Director->GetPatrolShip();
	TestNotNull(TEXT("climax patrol ship"), Ship);
	if (!Ship)
	{
		World->DestroyWorld(false);
		return false;
	}

	USkyguardRadioChatterComponent* ShipRadio =
		AttachRadio(Ship, TEXT("HarborPatrolShipSystemsRadio"));
	TestNotNull(TEXT("ship radio"), ShipRadio);
	if (!ShipRadio)
	{
		World->DestroyWorld(false);
		return false;
	}

	const int32 RemainingCount = UE_ARRAY_COUNT(GRemainingShipSystemCalls);
	for (int32 Index = 0; Index < RemainingCount; ++Index)
	{
		const FHarborShipSystemCall& Call = GRemainingShipSystemCalls[Index];
		ShipRadio->ClearQueue();
		SkyguardPilotVoice::ResetCallProbe();
		Ship->ApplyHitToSystem(Call.System, 500.f);
		TestTrue(
			*FString::Printf(TEXT("%s is dead after ApplyHitToSystem"), Call.Label),
			Ship->IsSystemDead(Call.System));
		ExpectCallEventOnRadio(*this, ShipRadio, Call.Line, Call.Label);

		const bool bLastRemainingSystem = Index == RemainingCount - 1;
		if (bLastRemainingSystem)
		{
			// Public kill path: four destroyed systems defeat the hull.
			// KillPart fires ShipDead, then AnnounceSystemKill fires ShipDeckDown.
			TestTrue(TEXT("four remaining systems defeat the ship"), Ship->IsDefeated());
			TestEqual(
				TEXT("fourth kill CallEvent count is ShipDead then ShipDeckDown"),
				SkyguardPilotVoice::GetCalledEventCount(),
				2);
			ExpectSystemCopy(*this, ESkyguardPilotLine::ShipDead, TEXT("ShipDead"));
			TestEqual(
				TEXT("radio starts ShipDead before the queued ShipDeckDown"),
				ShipRadio->GetCurrentLineId(),
				SkyguardPilotVoice::MakeRadioLine(ESkyguardPilotLine::ShipDead).LineId);
			TestTrue(
				TEXT("ShipDeckDown is queued behind ShipDead"),
				ShipRadio->GetQueuedLineCount() >= 1);
		}
		else
		{
			TestFalse(TEXT("fewer than four systems keep the ship alive"), Ship->IsDefeated());
			TestEqual(
				TEXT("single-system CallEvent count"),
				SkyguardPilotVoice::GetCalledEventCount(),
				1);
		}
	}

	World->DestroyWorld(false);
	return true;
}

#endif
