#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgDebrief.h"
#include "SkyguardRadioChatterComponent.h"

#include "Misc/AutomationTest.h"

namespace SkyguardRadioChatterEmptyLineTests
{
	FSkyguardRadioLine MakeEmptyLine()
	{
		FSkyguardRadioLine Line;
		Line.LineId = NAME_None;
		Line.Speaker = FText::FromString(TEXT("Pilot"));
		Line.Subtitle = FText::GetEmpty();
		Line.Priority = 20;
		Line.EstimatedDurationSeconds = 0.4f;
		return Line;
	}

	FSkyguardRadioLine MakeValidLine()
	{
		FSkyguardRadioLine Line;
		Line.LineId = FName(TEXT("HoldOrbit"));
		Line.Speaker = FText::FromString(TEXT("Pilot"));
		Line.Subtitle = FText::FromString(TEXT("Hold the orbit."));
		Line.Priority = 20;
		Line.EstimatedDurationSeconds = 0.4f;
		return Line;
	}

	bool ExpectNoBannedCopy(
		FAutomationTestBase& Test,
		const FSkyguardRadioLine& Line,
		const TCHAR* Label)
	{
		const bool bLineIdClean = Test.TestFalse(
			*FString::Printf(TEXT("%s LineId bans Igla/Yak/rifle"), Label),
			SkyguardCpgCopyHasBannedTerm(Line.LineId.ToString()));
		const bool bSubtitleClean = Test.TestFalse(
			*FString::Printf(TEXT("%s subtitle bans Igla/Yak/rifle"), Label),
			SkyguardCpgCopyHasBannedTerm(Line.Subtitle.ToString()));
		return bLineIdClean && bSubtitleClean;
	}

	bool ExpectFreshCounts(FAutomationTestBase& Test, const USkyguardRadioChatterComponent* Radio)
	{
		return Test.TestEqual(TEXT("queued count is 0"), Radio->GetQueuedLineCount(), 0) &&
			Test.TestEqual(TEXT("current line is NAME_None"), Radio->GetCurrentLineId(), NAME_None) &&
			Test.TestEqual(TEXT("dropped count is 0"), Radio->GetDroppedLineCount(), 0) &&
			Test.TestEqual(TEXT("played count is 0"), Radio->GetPlayedLineCount(), 0);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadioEmptyLineFailClosedTest,
	"Skyguard52.Audio.Radio.EmptyLineFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadioEmptyLineFailClosedTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRadioChatterEmptyLineTests;

	USkyguardRadioChatterComponent* Radio = NewObject<USkyguardRadioChatterComponent>();
	TestNotNull(TEXT("radio"), Radio);
	if (!Radio)
	{
		return false;
	}

	TestTrue(TEXT("NewObject defaults are empty"), ExpectFreshCounts(*this, Radio));

	Radio->PrimeLines(TArray<FSkyguardRadioLine>());
	TestTrue(TEXT("PrimeLines({}) is a no-op"), ExpectFreshCounts(*this, Radio));

	const FSkyguardRadioLine Empty = MakeEmptyLine();
	TestTrue(TEXT("Empty line copy is clean"), ExpectNoBannedCopy(*this, Empty, TEXT("Empty")));
	TestTrue(TEXT("Empty LineId is NAME_None"), Empty.LineId.IsNone());

	TestFalse(TEXT("NAME_None LineId is rejected"), Radio->EnqueueLine(Empty));
	TestEqual(TEXT("NAME_None increments dropped by 1"), Radio->GetDroppedLineCount(), 1);
	TestEqual(TEXT("NAME_None leaves the queue empty"), Radio->GetQueuedLineCount(), 0);
	TestEqual(TEXT("NAME_None leaves current line NAME_None"), Radio->GetCurrentLineId(), NAME_None);
	TestEqual(TEXT("NAME_None does not increment played"), Radio->GetPlayedLineCount(), 0);

	const FSkyguardRadioLine Valid = MakeValidLine();
	TestTrue(TEXT("Valid line copy is clean"), ExpectNoBannedCopy(*this, Valid, TEXT("Valid")));
	TestTrue(TEXT("Valid LineId is not NAME_None"), !Valid.LineId.IsNone());

	TestTrue(TEXT("Valid LineId after NAME_None drop is accepted"), Radio->EnqueueLine(Valid));
	TestEqual(TEXT("Valid line starts immediately"), Radio->GetCurrentLineId(), Valid.LineId);
	TestEqual(TEXT("Valid line is not left queued"), Radio->GetQueuedLineCount(), 0);
	TestEqual(TEXT("Dropped stays at 1 after valid enqueue"), Radio->GetDroppedLineCount(), 1);
	TestEqual(TEXT("Valid line increments played"), Radio->GetPlayedLineCount(), 1);

	return true;
}

#endif
