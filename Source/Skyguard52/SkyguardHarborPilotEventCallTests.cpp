#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgDebrief.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardPatrolShipBoss.h"
#include "SkyguardPilotVoice.h"
#include "SkyguardProtectAsset.h"
#include "SkyguardRadioChatterComponent.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace
{
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

	bool ExpectFamilyCopy(FAutomationTestBase& Test, const ESkyguardPilotLine Line)
	{
		const FString Text = SkyguardPilotVoice::LineTextForEvent(Line);
		return Test.TestFalse(TEXT("Harbor event copy stays non-empty"), Text.IsEmpty()) &&
			Test.TestFalse(
				TEXT("Harbor event copy bans Igla/Yak/rifle"),
				SkyguardCpgCopyHasBannedTerm(Text));
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborPilotEventFamiliesMapToCallEventsTest,
	"Skyguard52.Campaign.Harbor.PilotEventFamiliesMapToCallEvents",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborPilotEventFamiliesMapToCallEventsTest::RunTest(
	const FString& Parameters)
{
	const ESkyguardPilotLine ShipSightedFamily[] = {
		ESkyguardPilotLine::ShipRadarDown,
		ESkyguardPilotLine::ShipCannonDown,
		ESkyguardPilotLine::ShipLauncherDown,
		ESkyguardPilotLine::ShipEnginesDown,
		ESkyguardPilotLine::ShipDeckDown,
		ESkyguardPilotLine::ShipDead};
	const ESkyguardPilotLine CargoThreatFamily[] = {
		ESkyguardPilotLine::CargoHit,
		ESkyguardPilotLine::CargoCritical};
	const ESkyguardPilotLine FlareFamily[] = {ESkyguardPilotLine::FlaresGood};
	const ESkyguardPilotLine WinFailFamily[] = {
		ESkyguardPilotLine::Win,
		ESkyguardPilotLine::Fail};

	for (const ESkyguardPilotLine Line : ShipSightedFamily)
	{
		ExpectFamilyCopy(*this, Line);
	}
	for (const ESkyguardPilotLine Line : CargoThreatFamily)
	{
		ExpectFamilyCopy(*this, Line);
	}
	for (const ESkyguardPilotLine Line : FlareFamily)
	{
		ExpectFamilyCopy(*this, Line);
	}
	for (const ESkyguardPilotLine Line : WinFailFamily)
	{
		ExpectFamilyCopy(*this, Line);
	}

	TestEqual(
		TEXT("flare CallEvent name is FlaresGood"),
		SkyguardPilotVoice::MakeRadioLine(ESkyguardPilotLine::FlaresGood).LineId,
		FName(TEXT("FlaresGood")));
	TestEqual(
		TEXT("win CallEvent name is Win"),
		SkyguardPilotVoice::MakeRadioLine(ESkyguardPilotLine::Win).LineId,
		FName(TEXT("Win")));
	TestEqual(
		TEXT("fail CallEvent name is Fail"),
		SkyguardPilotVoice::MakeRadioLine(ESkyguardPilotLine::Fail).LineId,
		FName(TEXT("Fail")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborPilotEventFamiliesEnqueueOnRadioTest,
	"Skyguard52.Campaign.Harbor.PilotEventFamiliesEnqueueOnRadio",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborPilotEventFamiliesEnqueueOnRadioTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardHarborPilotEventRadioWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Host =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("host"), Host);
	USkyguardRadioChatterComponent* Radio =
		AttachRadio(Host, TEXT("HarborPilotEventRadio"));
	TestNotNull(TEXT("radio"), Radio);
	if (!Host || !Radio)
	{
		World->DestroyWorld(false);
		return false;
	}
	Host->bAutoStart = false;

	const ESkyguardPilotLine Families[] = {
		ESkyguardPilotLine::ShipRadarDown,
		ESkyguardPilotLine::ShipDead,
		ESkyguardPilotLine::CargoHit,
		ESkyguardPilotLine::CargoCritical,
		ESkyguardPilotLine::FlaresGood,
		ESkyguardPilotLine::Win,
		ESkyguardPilotLine::Fail};
	const TCHAR* Labels[] = {
		TEXT("ship-sighted ShipRadarDown"),
		TEXT("ship-sighted ShipDead"),
		TEXT("cargo-threat CargoHit"),
		TEXT("cargo-threat CargoCritical"),
		TEXT("flare FlaresGood"),
		TEXT("win Win"),
		TEXT("fail Fail")};
	for (int32 Index = 0; Index < UE_ARRAY_COUNT(Families); ++Index)
	{
		Radio->ClearQueue();
		SkyguardPilotVoice::ResetCallProbe();
		SkyguardPilotVoice::CallEvent(Host, Families[Index]);
		ExpectCallEventOnRadio(*this, Radio, Families[Index], Labels[Index]);
	}

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborDirectorShipAndCargoFireCallEventsTest,
	"Skyguard52.Campaign.Harbor.DirectorShipAndCargoFireCallEvents",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborDirectorShipAndCargoFireCallEventsTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardHarborPilotEventShipCargoWorld"));
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

	ASkyguardProtectAsset* Cargo = Director->GetCargoAsset();
	TestNotNull(TEXT("harbor cargo"), Cargo);
	USkyguardRadioChatterComponent* DirectorRadio =
		AttachRadio(Director, TEXT("HarborCargoPilotRadio"));
	TestNotNull(TEXT("director radio"), DirectorRadio);
	if (!Cargo || !DirectorRadio)
	{
		World->DestroyWorld(false);
		return false;
	}

	SkyguardPilotVoice::ResetCallProbe();
	Cargo->ApplyDamage(10.f);
	Director->Tick(0.01f);
	TestEqual(
		TEXT("cargo-threat CallEvent CargoHit"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::CargoHit);
	ExpectCallEventOnRadio(
		*this, DirectorRadio, ESkyguardPilotLine::CargoHit, TEXT("director CargoHit"));

	DirectorRadio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	Cargo->ApplyDamage(60.f);
	Director->Tick(0.01f);
	TestEqual(
		TEXT("cargo-threat CallEvent CargoCritical"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::CargoCritical);
	ExpectCallEventOnRadio(
		*this,
		DirectorRadio,
		ESkyguardPilotLine::CargoCritical,
		TEXT("director CargoCritical"));

	// Harbor BeatSeconds: 120 / 240 / 360 / 480 / 600. No gunner, so inbound
	// never arms and these ticks only advance beats / spawn the patrol ship.
	Director->Tick(120.f);
	Director->Tick(120.f);
	Director->Tick(120.f);
	Director->Tick(120.f);
	Director->Tick(120.f);
	TestEqual(
		TEXT("fifth gate is Climax — ship is sighted"),
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
		AttachRadio(Ship, TEXT("HarborShipPilotRadio"));
	TestNotNull(TEXT("ship radio"), ShipRadio);
	SkyguardPilotVoice::ResetCallProbe();
	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Radar, 500.f);
	TestEqual(
		TEXT("ship-sighted CallEvent ShipRadarDown"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::ShipRadarDown);
	ExpectCallEventOnRadio(
		*this,
		ShipRadio,
		ESkyguardPilotLine::ShipRadarDown,
		TEXT("director ship-sighted"));

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborDirectorFlareAndWinFailFireCallEventsTest,
	"Skyguard52.Campaign.Harbor.DirectorFlareAndWinFailFireCallEvents",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborDirectorFlareAndWinFailFireCallEventsTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardHarborPilotEventFlareWinWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	TestNotNull(TEXT("director"), Director);
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Director || !Gunner)
	{
		World->DestroyWorld(false);
		return false;
	}

	USkyguardRadioChatterComponent* Radio =
		AttachRadio(Director, TEXT("HarborFlareWinPilotRadio"));
	TestNotNull(TEXT("radio"), Radio);
	Director->bAutoStart = false;
	Director->StartMissionIndex(1);

	// Leave Approach without burning the 2.6s inbound window on the same tick.
	Director->Tick(119.f);
	TestEqual(
		TEXT("still on approach before the first beat gate"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Approach);
	Director->Tick(1.1f);
	TestEqual(
		TEXT("first gate is contact — inbound can arm"),
		Director->GetBeat(),
		ESkyguardSortieBeat::InitialContact);
	TestTrue(TEXT("director armed an inbound"), Gunner->IsMissileInbound());

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	Gunner->PopFlares();
	Director->Tick(0.1f);
	TestEqual(
		TEXT("flare CallEvent FlaresGood"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::FlaresGood);
	ExpectCallEventOnRadio(
		*this, Radio, ESkyguardPilotLine::FlaresGood, TEXT("director FlaresGood"));
	TestFalse(TEXT("flare cleared the inbound"), Gunner->IsMissileInbound());

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	Director->ResolveSortie(true);
	TestEqual(
		TEXT("win leaves LoadoutPrompt last on the probe"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::LoadoutPrompt);
	TestTrue(
		TEXT("win CallEvent fired before the loadout prompt"),
		SkyguardPilotVoice::GetCalledEventCount() >= 2);
	TestEqual(
		TEXT("win CallEvent name on radio"),
		Radio->GetCurrentLineId(),
		SkyguardPilotVoice::MakeRadioLine(ESkyguardPilotLine::Win).LineId);
	TestFalse(
		TEXT("win copy bans Igla/Yak/rifle"),
		SkyguardCpgCopyHasBannedTerm(
			SkyguardPilotVoice::LineTextForEvent(ESkyguardPilotLine::Win)));

	Director->StartMissionIndex(1);
	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	Director->ResolveSortie(false, TEXT("Harbor fail radio"));
	TestEqual(
		TEXT("fail leaves LoadoutPrompt last on the probe"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::LoadoutPrompt);
	TestTrue(
		TEXT("fail CallEvent fired before the loadout prompt"),
		SkyguardPilotVoice::GetCalledEventCount() >= 2);
	TestEqual(
		TEXT("fail CallEvent name on radio"),
		Radio->GetCurrentLineId(),
		SkyguardPilotVoice::MakeRadioLine(ESkyguardPilotLine::Fail).LineId);
	TestFalse(
		TEXT("fail copy bans Igla/Yak/rifle"),
		SkyguardCpgCopyHasBannedTerm(
			SkyguardPilotVoice::LineTextForEvent(ESkyguardPilotLine::Fail)));

	World->DestroyWorld(false);
	return true;
}

#endif
