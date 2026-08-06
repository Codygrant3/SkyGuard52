#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardRadioChatterComponent.h"
#include "Misc/AutomationTest.h"

namespace
{
	FSkyguardRadioLine MakeLine(const TCHAR* Id, const int32 Priority, const float Duration = 0.25f)
	{
		FSkyguardRadioLine Line;
		Line.LineId = FName(Id);
		Line.Priority = Priority;
		Line.EstimatedDurationSeconds = Duration;
		return Line;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadioQueueTest,
	"Skyguard52.Audio.Radio.BoundedPriorityQueue",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadioQueueTest::RunTest(const FString& Parameters)
{
	USkyguardRadioChatterComponent* Radio = NewObject<USkyguardRadioChatterComponent>();
	Radio->MaxQueuedLines = 2;
	Radio->InterLineGapSeconds = 0.f;

	TestTrue(TEXT("First radio line starts immediately"), Radio->EnqueueLine(MakeLine(TEXT("Routine"), 10)));
	TestEqual(TEXT("Routine line is current"), Radio->GetCurrentLineId(), FName(TEXT("Routine")));
	TestTrue(TEXT("Second line queues"), Radio->EnqueueLine(MakeLine(TEXT("Advisory"), 20)));
	TestTrue(TEXT("Third line queues"), Radio->EnqueueLine(MakeLine(TEXT("Navigation"), 30)));
	TestTrue(TEXT("Critical line replaces the lowest queued priority"),
		Radio->EnqueueLine(MakeLine(TEXT("MissileWarning"), 100)));
	TestEqual(TEXT("Queue never exceeds its budget"), Radio->GetQueuedLineCount(), 2);
	TestEqual(TEXT("Displaced line is reported"), Radio->GetDroppedLineCount(), 1);

	Radio->AdvanceRadioState(0.3f);
	TestEqual(TEXT("Critical line plays first after current line"), Radio->GetCurrentLineId(), FName(TEXT("MissileWarning")));
	Radio->AdvanceRadioState(0.3f);
	TestEqual(TEXT("Next-highest retained line plays next"), Radio->GetCurrentLineId(), FName(TEXT("Navigation")));
	Radio->AdvanceRadioState(0.3f);
	TestEqual(TEXT("Queue drains deterministically"), Radio->GetQueuedLineCount(), 0);
	TestEqual(TEXT("All accepted playback starts are counted"), Radio->GetPlayedLineCount(), 3);

	FSkyguardRadioLine CooldownLine = MakeLine(TEXT("LockWarning"), 90);
	CooldownLine.CooldownSeconds = 1.f;
	TestTrue(TEXT("Cooldown line is initially accepted"), Radio->EnqueueLine(CooldownLine));
	TestFalse(TEXT("Same line is rejected while cooling down"), Radio->EnqueueLine(CooldownLine));
	Radio->AdvanceRadioState(1.1f);
	TestTrue(TEXT("Same line can return after cooldown"), Radio->EnqueueLine(CooldownLine));

	return true;
}

#endif

