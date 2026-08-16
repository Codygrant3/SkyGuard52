#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgDebrief.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardHarborBeatCalls.h"
#include "SkyguardPilotVoice.h"
#include "SkyguardRadioChatterComponent.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace
{
	USkyguardRadioChatterComponent* AttachRadio(AActor* Owner)
	{
		if (!Owner)
		{
			return nullptr;
		}
		USkyguardRadioChatterComponent* Radio = NewObject<USkyguardRadioChatterComponent>(
			Owner,
			USkyguardRadioChatterComponent::StaticClass(),
			TEXT("HarborPilotRadio"),
			RF_Transient);
		Radio->RegisterComponent();
		Radio->InterLineGapSeconds = 0.f;
		return Radio;
	}

	bool ExpectLineOnRadio(
		FAutomationTestBase& Test,
		USkyguardRadioChatterComponent* Radio,
		const ESkyguardPilotLine Line,
		const TCHAR* Label)
	{
		const FSkyguardRadioLine Built = SkyguardPilotVoice::MakeRadioLine(Line);
		const bool bOk =
			Test.TestEqual(
				*FString::Printf(TEXT("%s line id"), Label),
				Radio->GetCurrentLineId(),
				Built.LineId) &&
			Test.TestTrue(
				*FString::Printf(TEXT("%s played"), Label),
				Radio->GetPlayedLineCount() >= 1) &&
			Test.TestFalse(
				*FString::Printf(TEXT("%s bans Igla/Yak/rifle"), Label),
				SkyguardCpgCopyHasBannedTerm(Built.Subtitle.ToString())) &&
			Test.TestFalse(
				*FString::Printf(TEXT("%s raw text bans Igla/Yak/rifle"), Label),
				SkyguardCpgCopyHasBannedTerm(SkyguardPilotVoice::LineTextForEvent(Line)));
		return bOk;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborBeatCallsMapToPilotLinesTest,
	"Skyguard52.Campaign.Harbor.BeatCallsMapToPilotLines",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborBeatCallsMapToPilotLinesTest::RunTest(const FString& Parameters)
{
	ESkyguardPilotLine Line = ESkyguardPilotLine::Win;
	TestTrue(
		TEXT("RadarNet maps to RadarLit"),
		SkyguardHarborBeatCalls::TryLineForBeat(ESkyguardSortieBeat::RadarNet, Line));
	TestEqual(TEXT("RadarLit"), Line, ESkyguardPilotLine::RadarLit);

	TestTrue(
		TEXT("Choice maps to Choice"),
		SkyguardHarborBeatCalls::TryLineForBeat(ESkyguardSortieBeat::Choice, Line));
	TestEqual(TEXT("Choice"), Line, ESkyguardPilotLine::Choice);

	TestTrue(
		TEXT("Extraction maps to Extract"),
		SkyguardHarborBeatCalls::TryLineForBeat(ESkyguardSortieBeat::Extraction, Line));
	TestEqual(TEXT("Extract"), Line, ESkyguardPilotLine::Extract);

	TestFalse(
		TEXT("Approach has no Harbor beat call"),
		SkyguardHarborBeatCalls::TryLineForBeat(ESkyguardSortieBeat::Approach, Line));
	TestEqual(
		TEXT("Inbound event line"),
		SkyguardHarborBeatCalls::InboundLine(),
		ESkyguardPilotLine::Inbound);
	TestEqual(
		TEXT("Night thermal event line"),
		SkyguardHarborBeatCalls::GoThermalLine(),
		ESkyguardPilotLine::GoThermal);

	const ESkyguardPilotLine HarborLines[] = {
		ESkyguardPilotLine::RadarLit,
		ESkyguardPilotLine::Inbound,
		ESkyguardPilotLine::Choice,
		ESkyguardPilotLine::Extract,
		ESkyguardPilotLine::GoThermal};
	for (const ESkyguardPilotLine HarborLine : HarborLines)
	{
		const FString Text = SkyguardPilotVoice::LineTextForEvent(HarborLine);
		TestFalse(
			TEXT("Harbor pilot copy stays non-empty"),
			Text.IsEmpty());
		TestFalse(
			TEXT("Harbor pilot copy bans Igla/Yak/rifle"),
			SkyguardCpgCopyHasBannedTerm(Text));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborBeatCallsEnqueueOnRadioTest,
	"Skyguard52.Campaign.Harbor.BeatCallsEnqueueOnRadio",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborBeatCallsEnqueueOnRadioTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardHarborBeatRadioWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Host =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("host"), Host);
	USkyguardRadioChatterComponent* Radio = AttachRadio(Host);
	TestNotNull(TEXT("radio"), Radio);
	if (!Host || !Radio)
	{
		World->DestroyWorld(false);
		return false;
	}
	Host->bAutoStart = false;

	SkyguardPilotVoice::ResetCallProbe();
	TestTrue(
		TEXT("RadarNet applies"),
		SkyguardHarborBeatCalls::ApplyBeat(
			Host, ESkyguardSortieBeat::RadarNet, Radio));
	TestEqual(
		TEXT("probe RadarLit"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::RadarLit);
	ExpectLineOnRadio(*this, Radio, ESkyguardPilotLine::RadarLit, TEXT("RadarLit"));

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	TestTrue(
		TEXT("Choice applies"),
		SkyguardHarborBeatCalls::ApplyBeat(
			Host, ESkyguardSortieBeat::Choice, Radio));
	TestEqual(
		TEXT("probe Choice"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::Choice);
	ExpectLineOnRadio(*this, Radio, ESkyguardPilotLine::Choice, TEXT("Choice"));

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	TestTrue(
		TEXT("Extract applies"),
		SkyguardHarborBeatCalls::ApplyBeat(
			Host, ESkyguardSortieBeat::Extraction, Radio));
	TestEqual(
		TEXT("probe Extract"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::Extract);
	ExpectLineOnRadio(*this, Radio, ESkyguardPilotLine::Extract, TEXT("Extract"));

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	TestTrue(
		TEXT("Inbound applies"),
		SkyguardHarborBeatCalls::ApplyInbound(Host, Radio));
	TestEqual(
		TEXT("probe Inbound"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::Inbound);
	ExpectLineOnRadio(*this, Radio, ESkyguardPilotLine::Inbound, TEXT("Inbound"));

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	TestTrue(
		TEXT("GoThermal applies"),
		SkyguardHarborBeatCalls::ApplyGoThermal(Host, Radio));
	TestEqual(
		TEXT("probe GoThermal"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::GoThermal);
	ExpectLineOnRadio(*this, Radio, ESkyguardPilotLine::GoThermal, TEXT("GoThermal"));

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborDirectorBeatsFirePilotCallsTest,
	"Skyguard52.Campaign.Harbor.DirectorBeatsFirePilotCalls",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborDirectorBeatsFirePilotCallsTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardHarborDirectorPilotWorld"));
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

	USkyguardRadioChatterComponent* Radio = AttachRadio(Director);
	TestNotNull(TEXT("radio on director"), Radio);
	Director->bAutoStart = false;
	Director->StartMissionIndex(1);

	// Harbor BeatSeconds: 120 / 240 / 360 / 480 / 600 / 780.
	// AdvanceBeats moves one step per Tick when Elapsed crosses the next gate.
	SkyguardPilotVoice::ResetCallProbe();
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
	Director->Tick(120.f);
	TestEqual(
		TEXT("third gate is RadarNet"),
		Director->GetBeat(),
		ESkyguardSortieBeat::RadarNet);
	TestEqual(
		TEXT("RadarNet CallEvent RadarLit"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::RadarLit);
	ExpectLineOnRadio(*this, Radio, ESkyguardPilotLine::RadarLit, TEXT("director RadarLit"));

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	Director->Tick(120.f);
	TestEqual(
		TEXT("fourth gate is Choice"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Choice);
	TestEqual(
		TEXT("Choice CallEvent Choice"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::Choice);
	ExpectLineOnRadio(*this, Radio, ESkyguardPilotLine::Choice, TEXT("director Choice"));

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
		TEXT("Extraction CallEvent Extract"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::Extract);
	ExpectLineOnRadio(*this, Radio, ESkyguardPilotLine::Extract, TEXT("director Extract"));

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	SkyguardPilotVoice::CallEvent(Director, ESkyguardPilotLine::Inbound);
	TestEqual(
		TEXT("Inbound CallEvent"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::Inbound);
	ExpectLineOnRadio(*this, Radio, ESkyguardPilotLine::Inbound, TEXT("director Inbound"));

	Radio->ClearQueue();
	SkyguardPilotVoice::ResetCallProbe();
	SkyguardPilotVoice::CallEvent(Director, ESkyguardPilotLine::GoThermal);
	TestEqual(
		TEXT("GoThermal CallEvent"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::GoThermal);
	ExpectLineOnRadio(*this, Radio, ESkyguardPilotLine::GoThermal, TEXT("director GoThermal"));

	World->DestroyWorld(false);
	return true;
}

#endif
