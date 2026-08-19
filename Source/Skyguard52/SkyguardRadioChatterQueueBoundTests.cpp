#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgDebrief.h"
#include "SkyguardRadioChatterComponent.h"

#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Misc/AutomationTest.h"

namespace SkyguardRadioChatterQueueBoundTests
{
	FSkyguardRadioLine MakeLine(
		const TCHAR* Id,
		const TCHAR* Subtitle,
		const int32 Priority,
		const float DurationSeconds = 0.4f)
	{
		FSkyguardRadioLine Line;
		Line.LineId = FName(Id);
		Line.Speaker = FText::FromString(TEXT("Pilot"));
		Line.Subtitle = FText::FromString(Subtitle);
		Line.Priority = Priority;
		Line.EstimatedDurationSeconds = DurationSeconds;
		return Line;
	}

	USkyguardRadioChatterComponent* AttachRadio(AActor* Owner)
	{
		if (!Owner)
		{
			return nullptr;
		}
		USkyguardRadioChatterComponent* Radio = NewObject<USkyguardRadioChatterComponent>(
			Owner,
			USkyguardRadioChatterComponent::StaticClass(),
			TEXT("QueueBoundRadio"),
			RF_Transient);
		Radio->RegisterComponent();
		Radio->MaxQueuedLines = 4;
		Radio->InterLineGapSeconds = 0.f;
		return Radio;
	}

	bool ExpectNoBannedCopy(
		FAutomationTestBase& Test,
		const FSkyguardRadioLine& Line,
		const TCHAR* Label)
	{
		return Test.TestFalse(
			*FString::Printf(TEXT("%s subtitle bans Igla/Yak/rifle"), Label),
			SkyguardCpgCopyHasBannedTerm(Line.Subtitle.ToString()));
	}

	bool ExpectQueueWithinCap(
		FAutomationTestBase& Test,
		const USkyguardRadioChatterComponent* Radio)
	{
		return Test.TestTrue(
			TEXT("Queued count never exceeds MaxQueuedLines"),
			Radio->GetQueuedLineCount() <= Radio->MaxQueuedLines);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadioQueueDropsOverflowPastCapTest,
	"Skyguard52.Audio.Radio.QueueDropsOverflowPastCap",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadioQueueDropsOverflowPastCapTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRadioChatterQueueBoundTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardRadioQueueBoundOverflowWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	AActor* Host = World->SpawnActor<AActor>();
	USkyguardRadioChatterComponent* Radio = AttachRadio(Host);
	TestNotNull(TEXT("host"), Host);
	TestNotNull(TEXT("radio"), Radio);
	if (!Host || !Radio)
	{
		World->DestroyWorld(false);
		return false;
	}

	TestEqual(TEXT("MaxQueuedLines is the small cap"), Radio->MaxQueuedLines, 4);
	TestEqual(TEXT("Inter-line gap starts at zero"), Radio->InterLineGapSeconds, 0.f);
	TestEqual(TEXT("Queue starts empty"), Radio->GetQueuedLineCount(), 0);
	TestEqual(TEXT("Dropped starts at zero"), Radio->GetDroppedLineCount(), 0);

	const FSkyguardRadioLine Cannon = MakeLine(
		TEXT("CannonOnBoat"), TEXT("Thirty mil on the boat."), 20);
	const FSkyguardRadioLine Hydra = MakeLine(
		TEXT("HydraLaunchers"), TEXT("Hydra ripple on the launchers."), 20);
	const FSkyguardRadioLine Hellfire = MakeLine(
		TEXT("HellfireArmor"), TEXT("Hellfire, that is armor."), 20);
	const FSkyguardRadioLine Orbit = MakeLine(
		TEXT("HoldOrbit"), TEXT("Hold the orbit."), 20);
	const FSkyguardRadioLine Popup = MakeLine(
		TEXT("BreakPopup"), TEXT("Break left, then pop-up."), 20);
	const FSkyguardRadioLine Cargo = MakeLine(
		TEXT("KeepCargo"), TEXT("Keep the cargo."), 20);
	const FSkyguardRadioLine Extra = MakeLine(
		TEXT("ExtraContact"), TEXT("New contact, stay on the boat."), 20);

	TestTrue(TEXT("Cannon subtitle is clean"), ExpectNoBannedCopy(*this, Cannon, TEXT("Cannon")));
	TestTrue(TEXT("Hydra subtitle is clean"), ExpectNoBannedCopy(*this, Hydra, TEXT("Hydra")));
	TestTrue(TEXT("Hellfire subtitle is clean"), ExpectNoBannedCopy(*this, Hellfire, TEXT("Hellfire")));
	TestTrue(TEXT("Orbit subtitle is clean"), ExpectNoBannedCopy(*this, Orbit, TEXT("Orbit")));
	TestTrue(TEXT("Popup subtitle is clean"), ExpectNoBannedCopy(*this, Popup, TEXT("Popup")));
	TestTrue(TEXT("Cargo subtitle is clean"), ExpectNoBannedCopy(*this, Cargo, TEXT("Cargo")));
	TestTrue(TEXT("Extra subtitle is clean"), ExpectNoBannedCopy(*this, Extra, TEXT("Extra")));

	TestTrue(TEXT("First line starts immediately"), Radio->EnqueueLine(Cannon));
	TestEqual(TEXT("Playing line is not counted as queued"), Radio->GetQueuedLineCount(), 0);
	TestTrue(TEXT("After first enqueue"), ExpectQueueWithinCap(*this, Radio));

	TestTrue(TEXT("Hydra queues"), Radio->EnqueueLine(Hydra));
	TestTrue(TEXT("Hellfire queues"), Radio->EnqueueLine(Hellfire));
	TestTrue(TEXT("Orbit queues"), Radio->EnqueueLine(Orbit));
	TestTrue(TEXT("Popup fills the cap"), Radio->EnqueueLine(Popup));
	TestEqual(TEXT("Queue sits at the cap"), Radio->GetQueuedLineCount(), Radio->MaxQueuedLines);
	TestEqual(TEXT("No overflow yet"), Radio->GetDroppedLineCount(), 0);
	TestTrue(TEXT("At cap"), ExpectQueueWithinCap(*this, Radio));

	TestFalse(TEXT("Same-priority overflow is dropped"), Radio->EnqueueLine(Cargo));
	TestEqual(TEXT("First overflow increments dropped"), Radio->GetDroppedLineCount(), 1);
	TestEqual(TEXT("Queue stays at the cap after first drop"), Radio->GetQueuedLineCount(), 4);
	TestTrue(TEXT("After first drop"), ExpectQueueWithinCap(*this, Radio));

	TestFalse(TEXT("Further overflow is also dropped"), Radio->EnqueueLine(Extra));
	TestEqual(TEXT("Second overflow increments dropped again"), Radio->GetDroppedLineCount(), 2);
	TestEqual(TEXT("Queue still does not grow"), Radio->GetQueuedLineCount(), 4);
	TestTrue(TEXT("After second drop"), ExpectQueueWithinCap(*this, Radio));

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadioClearQueueZerosQueuedLinesTest,
	"Skyguard52.Audio.Radio.ClearQueueZerosQueuedLines",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadioClearQueueZerosQueuedLinesTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRadioChatterQueueBoundTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardRadioQueueBoundClearWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	AActor* Host = World->SpawnActor<AActor>();
	USkyguardRadioChatterComponent* Radio = AttachRadio(Host);
	TestNotNull(TEXT("host"), Host);
	TestNotNull(TEXT("radio"), Radio);
	if (!Host || !Radio)
	{
		World->DestroyWorld(false);
		return false;
	}

	const FSkyguardRadioLine Cannon = MakeLine(
		TEXT("CannonOnBoat"), TEXT("Thirty mil on the boat."), 20);
	const FSkyguardRadioLine Hydra = MakeLine(
		TEXT("HydraLaunchers"), TEXT("Hydra ripple on the launchers."), 20);
	const FSkyguardRadioLine Hellfire = MakeLine(
		TEXT("HellfireArmor"), TEXT("Hellfire, that is armor."), 20);
	TestTrue(TEXT("Cannon subtitle is clean"), ExpectNoBannedCopy(*this, Cannon, TEXT("Cannon")));
	TestTrue(TEXT("Hydra subtitle is clean"), ExpectNoBannedCopy(*this, Hydra, TEXT("Hydra")));
	TestTrue(TEXT("Hellfire subtitle is clean"), ExpectNoBannedCopy(*this, Hellfire, TEXT("Hellfire")));

	TestTrue(TEXT("Cannon accepted"), Radio->EnqueueLine(Cannon));
	TestTrue(TEXT("Hydra accepted"), Radio->EnqueueLine(Hydra));
	TestTrue(TEXT("Hellfire accepted"), Radio->EnqueueLine(Hellfire));
	TestTrue(TEXT("Queue has waiting lines before clear"), Radio->GetQueuedLineCount() > 0);

	Radio->ClearQueue();
	TestEqual(TEXT("ClearQueue zeros the queue"), Radio->GetQueuedLineCount(), 0);
	TestEqual(TEXT("ClearQueue stops the current line"), Radio->GetCurrentLineId(), NAME_None);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRadioAdvancePlaysThenGapsTest,
	"Skyguard52.Audio.Radio.AdvancePlaysThenGaps",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRadioAdvancePlaysThenGapsTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRadioChatterQueueBoundTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardRadioQueueBoundGapWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	AActor* Host = World->SpawnActor<AActor>();
	USkyguardRadioChatterComponent* Radio = AttachRadio(Host);
	TestNotNull(TEXT("host"), Host);
	TestNotNull(TEXT("radio"), Radio);
	if (!Host || !Radio)
	{
		World->DestroyWorld(false);
		return false;
	}

	const float PlaySeconds = 0.4f;
	const float GapSeconds = 0.25f;
	Radio->InterLineGapSeconds = GapSeconds;

	const FSkyguardRadioLine First = MakeLine(
		TEXT("CannonOnBoat"), TEXT("Thirty mil on the boat."), 40, PlaySeconds);
	const FSkyguardRadioLine Second = MakeLine(
		TEXT("HellfireArmor"), TEXT("Hellfire, that is armor."), 20, PlaySeconds);
	TestTrue(TEXT("First subtitle is clean"), ExpectNoBannedCopy(*this, First, TEXT("First")));
	TestTrue(TEXT("Second subtitle is clean"), ExpectNoBannedCopy(*this, Second, TEXT("Second")));

	TestTrue(TEXT("First line starts"), Radio->EnqueueLine(First));
	TestTrue(TEXT("Second line waits"), Radio->EnqueueLine(Second));
	TestEqual(TEXT("First line is current"), Radio->GetCurrentLineId(), First.LineId);
	TestEqual(TEXT("One line remains queued during play"), Radio->GetQueuedLineCount(), 1);
	TestTrue(TEXT("During play"), ExpectQueueWithinCap(*this, Radio));

	Radio->AdvanceRadioState(PlaySeconds * 0.5f);
	TestEqual(
		TEXT("Still playing before EstimatedDurationSeconds elapses"),
		Radio->GetCurrentLineId(),
		First.LineId);

	Radio->AdvanceRadioState(PlaySeconds);
	TestEqual(
		TEXT("After duration the line finishes and enters the inter-line gap"),
		Radio->GetCurrentLineId(),
		NAME_None);
	TestEqual(TEXT("Queued follower waits through the gap"), Radio->GetQueuedLineCount(), 1);

	Radio->AdvanceRadioState(GapSeconds * 0.4f);
	TestEqual(
		TEXT("Gap still holds the next line"),
		Radio->GetCurrentLineId(),
		NAME_None);

	Radio->AdvanceRadioState(GapSeconds);
	TestEqual(
		TEXT("After the gap the queued line plays"),
		Radio->GetCurrentLineId(),
		Second.LineId);
	TestEqual(TEXT("Queue drained into playback"), Radio->GetQueuedLineCount(), 0);
	TestTrue(TEXT("After gap start"), ExpectQueueWithinCap(*this, Radio));

	World->DestroyWorld(false);
	return true;
}

#endif
