#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardRadioChatterComponent.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardRadioChatterTests.cpp,
// SkyguardRadioChatterQueueBoundTests.cpp,
// SkyguardRadioChatterEmptyLineTests.cpp, and
// SkyguardRadioChatterEmptyQueueFailClosedTests.cpp.
// Remaining empty NewObject / CDO public defaults only.
// Existing siblings cover enqueue, empty-line enqueue, empty-queue
// ClearQueue / AdvanceRadioState no-ops, and bounded overflow.
// This file reads zero counts and CDO defaults. It does not call
// PrimeLines, EnqueueLine, AdvanceRadioState, ClearQueue,
// TickComponent, or EndPlay.
// NewObject only. No CreateWorld / SpawnActor.
// No Gunner / Yak / Igla / rifle live copy.
// Does not invent INDEX_NONE.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadioChatterEmptyFailClosedTest,
	"Skyguard52.Radio.EmptyFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadioChatterEmptyFailClosedTest::RunTest(const FString& Parameters)
{
	USkyguardRadioChatterComponent* Radio =
		NewObject<USkyguardRadioChatterComponent>(GetTransientPackage());
	TestNotNull(TEXT("NewObject empty radio chatter constructs"), Radio);
	if (!Radio)
	{
		return false;
	}

	TestEqual(TEXT("NewObject GetQueuedLineCount is 0"), Radio->GetQueuedLineCount(), 0);
	TestEqual(
		TEXT("NewObject GetCurrentLineId is NAME_None"),
		Radio->GetCurrentLineId(),
		NAME_None);
	TestEqual(TEXT("NewObject GetDroppedLineCount is 0"), Radio->GetDroppedLineCount(), 0);
	TestEqual(TEXT("NewObject GetPlayedLineCount is 0"), Radio->GetPlayedLineCount(), 0);
	TestEqual(TEXT("NewObject MaxQueuedLines is 16"), Radio->MaxQueuedLines, 16);
	TestEqual(
		TEXT("NewObject InterLineGapSeconds is 0.15"),
		Radio->InterLineGapSeconds,
		0.15f);

	return true;
}

#endif
