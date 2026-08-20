#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardObjectiveRuntime.h"

#include "Misc/AutomationTest.h"

namespace SkyguardObjectiveRuntimeFailClosedTests
{
	FSkyguardObjectiveDefinition MakeDestroyTargets(
		const FName ObjectiveId,
		const int32 RequiredProgress)
	{
		FSkyguardObjectiveDefinition Definition;
		Definition.ObjectiveId = ObjectiveId;
		Definition.DisplayName = FText::FromName(ObjectiveId);
		Definition.Type = ESkyguardMissionObjectiveType::DestroyTargets;
		Definition.RequiredProgress = RequiredProgress;
		Definition.bRequiredForMissionSuccess = true;
		Definition.bFailureEndsMission = false;
		return Definition;
	}

	bool ExpectEmptyStateContracts(
		FAutomationTestBase& Test,
		USkyguardObjectiveRuntime& Runtime)
	{
		const bool bRequiredIncomplete = Test.TestFalse(
			TEXT("empty definitions are not required-complete"),
			Runtime.AreRequiredObjectivesComplete());
		const bool bNoTerminal = Test.TestFalse(
			TEXT("empty definitions have no terminal failure"),
			Runtime.HasTerminalFailure());
		const bool bNoCompleted = Test.TestEqual(
			TEXT("empty completed set"),
			Runtime.GetCompletedObjectiveIds().Num(),
			0);

		const FSkyguardObjectiveProgress NoneProgress = Runtime.GetProgress(NAME_None);
		const bool bNoneId = Test.TestEqual(
			TEXT("GetProgress(NAME_None) ObjectiveId is NAME_None"),
			NoneProgress.ObjectiveId,
			NAME_None);
		const bool bNoneProgress = Test.TestEqual(
			TEXT("GetProgress(NAME_None) CurrentProgress is 0"),
			NoneProgress.CurrentProgress,
			0);
		const bool bNoneState = Test.TestEqual(
			TEXT("GetProgress(NAME_None) State is Inactive"),
			NoneProgress.State,
			ESkyguardMissionObjectiveState::Inactive);

		const bool bAddNone = Test.TestFalse(
			TEXT("AddProgress(NAME_None, 1) is rejected"),
			Runtime.AddProgress(NAME_None, 1));
		const bool bFailNone = Test.TestFalse(
			TEXT("FailObjective(NAME_None) is rejected"),
			Runtime.FailObjective(NAME_None));

		return bRequiredIncomplete && bNoTerminal && bNoCompleted && bNoneId &&
			bNoneProgress && bNoneState && bAddNone && bFailNone;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardObjectiveRuntimeUninitializedEmptyStateTest,
	"Skyguard52.Campaign.Runtime.ObjectiveEmptyStateWithoutInitialize",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardObjectiveRuntimeUninitializedEmptyStateTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardObjectiveRuntimeFailClosedTests;

	USkyguardObjectiveRuntime* Runtime = NewObject<USkyguardObjectiveRuntime>();
	TestNotNull(TEXT("uninitialized runtime is created"), Runtime);
	if (!Runtime)
	{
		return false;
	}

	return ExpectEmptyStateContracts(*this, *Runtime);
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardObjectiveRuntimeEmptyInitializeKeepsEmptyStateTest,
	"Skyguard52.Campaign.Runtime.ObjectiveEmptyInitializeKeepsEmptyState",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardObjectiveRuntimeEmptyInitializeKeepsEmptyStateTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardObjectiveRuntimeFailClosedTests;

	USkyguardObjectiveRuntime* Runtime = NewObject<USkyguardObjectiveRuntime>();
	TestNotNull(TEXT("empty-init runtime is created"), Runtime);
	if (!Runtime)
	{
		return false;
	}

	Runtime->InitializeObjectives({});
	return ExpectEmptyStateContracts(*this, *Runtime);
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardObjectiveRuntimeRejectsNonPositiveAddProgressTest,
	"Skyguard52.Campaign.Runtime.ObjectiveRejectsNonPositiveAddProgress",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardObjectiveRuntimeRejectsNonPositiveAddProgressTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardObjectiveRuntimeFailClosedTests;

	const FName DestroyId = TEXT("ClearTheRidge");
	USkyguardObjectiveRuntime* Runtime = NewObject<USkyguardObjectiveRuntime>();
	TestNotNull(TEXT("destroy runtime is created"), Runtime);
	if (!Runtime)
	{
		return false;
	}

	Runtime->InitializeObjectives({MakeDestroyTargets(DestroyId, 2)});

	TestFalse(TEXT("AddProgress(id, 0) is rejected"), Runtime->AddProgress(DestroyId, 0));
	const FSkyguardObjectiveProgress AfterZero = Runtime->GetProgress(DestroyId);
	TestEqual(TEXT("zero amount leaves CurrentProgress 0"), AfterZero.CurrentProgress, 0);
	TestEqual(
		TEXT("zero amount leaves State Active"),
		AfterZero.State,
		ESkyguardMissionObjectiveState::Active);

	TestFalse(TEXT("AddProgress(id, -1) is rejected"), Runtime->AddProgress(DestroyId, -1));
	const FSkyguardObjectiveProgress AfterNegative = Runtime->GetProgress(DestroyId);
	TestEqual(TEXT("negative amount leaves CurrentProgress 0"), AfterNegative.CurrentProgress, 0);
	TestEqual(
		TEXT("negative amount leaves State Active"),
		AfterNegative.State,
		ESkyguardMissionObjectiveState::Active);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardObjectiveRuntimeCompletedIdsExactAndLexicallySortedTest,
	"Skyguard52.Campaign.Runtime.ObjectiveCompletedIdsExactAndLexicallySorted",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardObjectiveRuntimeCompletedIdsExactAndLexicallySortedTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardObjectiveRuntimeFailClosedTests;

	const FName SingleId = TEXT("ClearTheRidge");
	USkyguardObjectiveRuntime* Single = NewObject<USkyguardObjectiveRuntime>();
	TestNotNull(TEXT("single-complete runtime is created"), Single);
	if (!Single)
	{
		return false;
	}

	Single->InitializeObjectives({MakeDestroyTargets(SingleId, 2)});
	TestTrue(TEXT("required progress of 2 completes in one accepted add"), Single->AddProgress(SingleId, 2));
	const TArray<FName> SingleCompleted = Single->GetCompletedObjectiveIds();
	TestEqual(TEXT("exactly one completed id"), SingleCompleted.Num(), 1);
	if (SingleCompleted.Num() == 1)
	{
		TestEqual(TEXT("completed id is the authored destroy id"), SingleCompleted[0], SingleId);
	}

	const FName LaterLexId = TEXT("ZuluClear");
	const FName EarlierLexId = TEXT("AlphaClear");
	USkyguardObjectiveRuntime* Pair = NewObject<USkyguardObjectiveRuntime>();
	TestNotNull(TEXT("two-complete runtime is created"), Pair);
	if (!Pair)
	{
		return false;
	}

	Pair->InitializeObjectives({
		MakeDestroyTargets(LaterLexId, 2),
		MakeDestroyTargets(EarlierLexId, 2)});
	TestTrue(TEXT("later lexical id completes first"), Pair->AddProgress(LaterLexId, 2));
	TestTrue(TEXT("earlier lexical id completes second"), Pair->AddProgress(EarlierLexId, 2));

	TArray<FName> Expected = {LaterLexId, EarlierLexId};
	Expected.Sort(FNameLexicalLess());
	const TArray<FName> PairCompleted = Pair->GetCompletedObjectiveIds();
	TestEqual(TEXT("exactly two completed ids"), PairCompleted.Num(), 2);
	TestEqual(TEXT("FNameLexicalLess puts Alpha before Zulu"), Expected.Num(), 2);
	if (Expected.Num() == 2)
	{
		TestEqual(TEXT("lexically first expected id"), Expected[0], EarlierLexId);
		TestEqual(TEXT("lexically second expected id"), Expected[1], LaterLexId);
	}
	if (PairCompleted.Num() == 2 && Expected.Num() == 2)
	{
		TestEqual(
			TEXT("GetCompletedObjectiveIds[0] matches FNameLexicalLess"),
			PairCompleted[0],
			Expected[0]);
		TestEqual(
			TEXT("GetCompletedObjectiveIds[1] matches FNameLexicalLess"),
			PairCompleted[1],
			Expected[1]);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardObjectiveRuntimeSurviveIntactRejectsNoneUnknownAndCompletedTest,
	"Skyguard52.Campaign.Runtime.SurviveIntactRejectsNoneUnknownAndCompleted",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardObjectiveRuntimeSurviveIntactRejectsNoneUnknownAndCompletedTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardObjectiveRuntimeFailClosedTests;

	const FName DestroyId = TEXT("ClearTheRidge");
	USkyguardObjectiveRuntime* Runtime = NewObject<USkyguardObjectiveRuntime>();
	TestNotNull(TEXT("survive-reject runtime is created"), Runtime);
	if (!Runtime)
	{
		return false;
	}

	Runtime->InitializeObjectives({MakeDestroyTargets(DestroyId, 2)});
	TestFalse(
		TEXT("CompleteSurviveObjectiveIfIntact(NAME_None) is rejected"),
		Runtime->CompleteSurviveObjectiveIfIntact(NAME_None));
	TestFalse(
		TEXT("CompleteSurviveObjectiveIfIntact(unknown id) is rejected"),
		Runtime->CompleteSurviveObjectiveIfIntact(TEXT("MissingObjective")));

	TestTrue(TEXT("destroy objective completes"), Runtime->AddProgress(DestroyId, 2));
	TestEqual(
		TEXT("completed destroy is Completed"),
		Runtime->GetProgress(DestroyId).State,
		ESkyguardMissionObjectiveState::Completed);
	TestFalse(
		TEXT("CompleteSurviveObjectiveIfIntact(already-completed id) is rejected"),
		Runtime->CompleteSurviveObjectiveIfIntact(DestroyId));
	TestEqual(
		TEXT("rejected intact-complete leaves CurrentProgress at required"),
		Runtime->GetProgress(DestroyId).CurrentProgress,
		2);
	TestEqual(
		TEXT("rejected intact-complete leaves State Completed"),
		Runtime->GetProgress(DestroyId).State,
		ESkyguardMissionObjectiveState::Completed);
	return true;
}

#endif
