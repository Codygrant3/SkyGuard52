#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardRadioChatterComponent.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardRadioChatterTests.cpp and
// SkyguardRadioChatterQueueBoundTests.cpp.
// Remaining empty-queue NewObject defaults / ClearQueue no-op /
// AdvanceRadioState empty no-op only.
// Does not call EnqueueLine / PrimeLines (those are sibling coverage).
// NewObject only. No world spawn, no Gunner / Yak / Igla / rifle.
// Does not invent INDEX_NONE.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadioChatterEmptyQueueFailClosedTest,
	"Skyguard52.Audio.Radio.EmptyQueueFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadioChatterEmptyQueueFailClosedTest::RunTest(const FString& Parameters)
{
	USkyguardRadioChatterComponent* Radio =
		NewObject<USkyguardRadioChatterComponent>();
	TestNotNull(TEXT("NewObject radio chatter constructs"), Radio);
	if (!Radio)
	{
		return false;
	}

	TestTrue(
		TEXT("Constructor enables PrimaryComponentTick.bCanEverTick"),
		Radio->PrimaryComponentTick.bCanEverTick);
	TestEqual(TEXT("NewObject MaxQueuedLines is 16"), Radio->MaxQueuedLines, 16);
	TestEqual(
		TEXT("NewObject InterLineGapSeconds is 0.15"),
		Radio->InterLineGapSeconds,
		0.15f);
	TestEqual(TEXT("NewObject GetQueuedLineCount is 0"), Radio->GetQueuedLineCount(), 0);
	TestEqual(TEXT("NewObject GetDroppedLineCount is 0"), Radio->GetDroppedLineCount(), 0);
	TestEqual(TEXT("NewObject GetPlayedLineCount is 0"), Radio->GetPlayedLineCount(), 0);
	TestEqual(
		TEXT("NewObject GetCurrentLineId is NAME_None"),
		Radio->GetCurrentLineId(),
		NAME_None);

	Radio->ClearQueue();

	TestEqual(
		TEXT("ClearQueue on empty queue leaves GetQueuedLineCount 0"),
		Radio->GetQueuedLineCount(),
		0);
	TestEqual(
		TEXT("ClearQueue on empty queue leaves GetDroppedLineCount 0"),
		Radio->GetDroppedLineCount(),
		0);
	TestEqual(
		TEXT("ClearQueue on empty queue leaves GetPlayedLineCount 0"),
		Radio->GetPlayedLineCount(),
		0);
	TestEqual(
		TEXT("ClearQueue on empty queue leaves GetCurrentLineId NAME_None"),
		Radio->GetCurrentLineId(),
		NAME_None);

	Radio->AdvanceRadioState(1.f);

	TestEqual(
		TEXT("AdvanceRadioState on empty queue leaves GetPlayedLineCount 0"),
		Radio->GetPlayedLineCount(),
		0);
	TestEqual(
		TEXT("AdvanceRadioState on empty queue leaves GetQueuedLineCount 0"),
		Radio->GetQueuedLineCount(),
		0);
	TestEqual(
		TEXT("AdvanceRadioState on empty queue leaves GetDroppedLineCount 0"),
		Radio->GetDroppedLineCount(),
		0);
	TestEqual(
		TEXT("AdvanceRadioState on empty queue leaves GetCurrentLineId NAME_None"),
		Radio->GetCurrentLineId(),
		NAME_None);

	return true;
}

#endif
