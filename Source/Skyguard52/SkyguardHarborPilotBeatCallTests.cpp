#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgDebrief.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardPilotVoice.h"
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
			Test.TestFalse(
				*FString::Printf(TEXT("%s LineId stays non-empty"), Label),
				Built.LineId.IsNone()) &&
			Test.TestFalse(
				*FString::Printf(TEXT("%s subtitle stays non-empty"), Label),
				Built.Subtitle.IsEmpty()) &&
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

	bool ExpectBeatFamilyCopy(FAutomationTestBase& Test, const ESkyguardPilotLine Line)
	{
		const FSkyguardRadioLine Built = SkyguardPilotVoice::MakeRadioLine(Line);
		const FString Text = SkyguardPilotVoice::LineTextForEvent(Line);
		return Test.TestFalse(TEXT("Harbor beat copy stays non-empty"), Text.IsEmpty()) &&
			Test.TestFalse(TEXT("Harbor beat LineId stays non-empty"), Built.LineId.IsNone()) &&
			Test.TestFalse(TEXT("Harbor beat subtitle stays non-empty"), Built.Subtitle.IsEmpty()) &&
			Test.TestFalse(
				TEXT("Harbor beat copy bans Igla/Yak/rifle"),
				SkyguardCpgCopyHasBannedTerm(Text)) &&
			Test.TestFalse(
				TEXT("Harbor beat subtitle bans Igla/Yak/rifle"),
				SkyguardCpgCopyHasBannedTerm(Built.Subtitle.ToString()));
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborPilotBeatFamiliesMapToCallEventsTest,
	"Skyguard52.Campaign.Harbor.PilotBeatFamiliesMapToCallEvents",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborPilotBeatFamiliesMapToCallEventsTest::RunTest(
	const FString& Parameters)
{
	const ESkyguardPilotLine BeatFamilies[] = {
		ESkyguardPilotLine::RadarLit,
		ESkyguardPilotLine::Inbound,
		ESkyguardPilotLine::Choice,
		ESkyguardPilotLine::Extract,
		ESkyguardPilotLine::GoThermal};
	for (const ESkyguardPilotLine Line : BeatFamilies)
	{
		ExpectBeatFamilyCopy(*this, Line);
	}

	TestEqual(
		TEXT("RadarLit CallEvent name"),
		SkyguardPilotVoice::MakeRadioLine(ESkyguardPilotLine::RadarLit).LineId,
		FName(TEXT("RadarLit")));
	TestEqual(
		TEXT("Inbound CallEvent name"),
		SkyguardPilotVoice::MakeRadioLine(ESkyguardPilotLine::Inbound).LineId,
		FName(TEXT("Inbound")));
	TestEqual(
		TEXT("Choice CallEvent name"),
		SkyguardPilotVoice::MakeRadioLine(ESkyguardPilotLine::Choice).LineId,
		FName(TEXT("Choice")));
	TestEqual(
		TEXT("Extract CallEvent name"),
		SkyguardPilotVoice::MakeRadioLine(ESkyguardPilotLine::Extract).LineId,
		FName(TEXT("Extract")));
	TestEqual(
		TEXT("GoThermal CallEvent name"),
		SkyguardPilotVoice::MakeRadioLine(ESkyguardPilotLine::GoThermal).LineId,
		FName(TEXT("GoThermal")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborPilotBeatFamiliesEnqueueOnRadioTest,
	"Skyguard52.Campaign.Harbor.PilotBeatFamiliesEnqueueOnRadio",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborPilotBeatFamiliesEnqueueOnRadioTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardHarborPilotBeatRadioWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Host =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("host"), Host);
	USkyguardRadioChatterComponent* Radio =
		AttachRadio(Host, TEXT("HarborPilotBeatRadio"));
	TestNotNull(TEXT("radio"), Radio);
	if (!Host || !Radio)
	{
		World->DestroyWorld(false);
		return false;
	}
	Host->bAutoStart = false;

	const ESkyguardPilotLine Families[] = {
		ESkyguardPilotLine::RadarLit,
		ESkyguardPilotLine::Inbound,
		ESkyguardPilotLine::Choice,
		ESkyguardPilotLine::Extract,
		ESkyguardPilotLine::GoThermal};
	const TCHAR* Labels[] = {
		TEXT("beat RadarLit"),
		TEXT("beat Inbound"),
		TEXT("beat Choice"),
		TEXT("beat Extract"),
		TEXT("beat GoThermal")};
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
	FSkyguardHarborDirectorBeatGatesFireCallEventsTest,
	"Skyguard52.Campaign.Harbor.DirectorBeatGatesFireCallEvents",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborDirectorBeatGatesFireCallEventsTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardHarborPilotBeatDirectorWorld"));
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

	USkyguardRadioChatterComponent* Radio =
		AttachRadio(Director, TEXT("HarborBeatGatePilotRadio"));
	TestNotNull(TEXT("radio"), Radio);
	Director->bAutoStart = false;
	SkyguardPilotVoice::ResetCallProbe();
	Director->StartMissionIndex(1);
	TestEqual(
		TEXT("harbor title"),
		Director->GetMissionTitle(),
		FString(TEXT("Harbor Breaker")));
	TestEqual(
		TEXT("Harbor overcast start does not CallEvent GoThermal"),
		SkyguardPilotVoice::GetCalledEventCount(),
		0);

	// Harbor BeatSeconds: 120 / 240 / 360 / 480 / 600 / 780.
	// No gunner, so TickIncoming returns before CallEvent(Inbound).
	Director->Tick(120.f);
	TestEqual(
		TEXT("first gate is contact"),
		Director->GetBeat(),
		ESkyguardSortieBeat::InitialContact);
	Director->Tick(120.f);
	TestEqual(
		TEXT("second gate is shore"),
		Director->GetBeat(),
		ESkyguardSortieBeat::ShoreAssault);

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	Director->Tick(120.f);
	TestEqual(
		TEXT("third gate is RadarNet"),
		Director->GetBeat(),
		ESkyguardSortieBeat::RadarNet);
	TestEqual(
		TEXT("RadarNet Tick CallEvent RadarLit"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::RadarLit);
	ExpectCallEventOnRadio(
		*this, Radio, ESkyguardPilotLine::RadarLit, TEXT("director RadarLit"));

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	Director->Tick(120.f);
	TestEqual(
		TEXT("fourth gate is Choice"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Choice);
	TestEqual(
		TEXT("Choice Tick CallEvent Choice"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::Choice);
	ExpectCallEventOnRadio(
		*this, Radio, ESkyguardPilotLine::Choice, TEXT("director Choice"));

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	Director->Tick(120.f);
	TestEqual(
		TEXT("fifth gate is Climax"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Climax);
	Director->Tick(180.f);
	TestEqual(
		TEXT("sixth gate is Extraction"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Extraction);
	TestEqual(
		TEXT("Extraction Tick CallEvent Extract"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::Extract);
	ExpectCallEventOnRadio(
		*this, Radio, ESkyguardPilotLine::Extract, TEXT("director Extract"));

	// GoThermal is CallEvent-only on Harbor (overcast, not night).
	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	SkyguardPilotVoice::CallEvent(Director, ESkyguardPilotLine::GoThermal);
	TestEqual(
		TEXT("GoThermal CallEvent mapping"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::GoThermal);
	ExpectCallEventOnRadio(
		*this, Radio, ESkyguardPilotLine::GoThermal, TEXT("CallEvent GoThermal"));

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborDirectorInboundFireCallEventTest,
	"Skyguard52.Campaign.Harbor.DirectorInboundFireCallEvent",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborDirectorInboundFireCallEventTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardHarborPilotBeatInboundWorld"));
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
		AttachRadio(Director, TEXT("HarborInboundPilotRadio"));
	TestNotNull(TEXT("radio"), Radio);
	Director->bAutoStart = false;
	Director->StartMissionIndex(1);

	// Leave Approach without burning the inbound window on the same tick.
	// Uses the existing first-delay clock. Does not retune 40/80 cadence.
	Director->Tick(119.f);
	TestEqual(
		TEXT("still on approach before the first beat gate"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Approach);
	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	Director->Tick(1.1f);
	TestEqual(
		TEXT("first gate is contact — inbound can arm"),
		Director->GetBeat(),
		ESkyguardSortieBeat::InitialContact);
	TestTrue(TEXT("director armed an inbound"), Gunner->IsMissileInbound());
	TestEqual(
		TEXT("contact Tick CallEvent Inbound"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::Inbound);
	ExpectCallEventOnRadio(
		*this, Radio, ESkyguardPilotLine::Inbound, TEXT("director Inbound"));

	World->DestroyWorld(false);
	return true;
}

#endif
