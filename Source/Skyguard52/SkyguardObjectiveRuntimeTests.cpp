#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardObjectiveRuntime.h"

#include "Misc/AutomationTest.h"

namespace SkyguardObjectiveRuntimeTests
{
	FSkyguardObjectiveDefinition MakeDestroy(
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

	FSkyguardObjectiveDefinition MakeSurviveProtect(
		const FName ObjectiveId,
		const ESkyguardMissionObjectiveType Type,
		const int32 RequiredProgress)
	{
		FSkyguardObjectiveDefinition Definition;
		Definition.ObjectiveId = ObjectiveId;
		Definition.DisplayName = FText::FromName(ObjectiveId);
		Definition.Type = Type;
		Definition.RequiredProgress = RequiredProgress;
		Definition.bRequiredForMissionSuccess = true;
		Definition.bFailureEndsMission = true;
		return Definition;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSurviveProtectCompletesOnlyWhileActiveTest,
	"Skyguard52.Objectives.Runtime.SurviveProtectCompletesOnlyWhileActive",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSurviveProtectCompletesOnlyWhileActiveTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardObjectiveRuntimeTests;

	USkyguardObjectiveRuntime* Runtime = NewObject<USkyguardObjectiveRuntime>();
	TestNotNull(TEXT("Objective runtime is created"), Runtime);
	if (!Runtime)
	{
		return false;
	}

	const TArray<FSkyguardObjectiveDefinition> Definitions = {
		MakeDestroy(TEXT("ClearThreats"), 2),
		MakeSurviveProtect(
			TEXT("ProtectFriendly"),
			ESkyguardMissionObjectiveType::ProtectAsset,
			3)
	};
	Runtime->InitializeObjectives(Definitions);

	TestFalse(
		TEXT("Required objectives start incomplete"),
		Runtime->AreRequiredObjectivesComplete());
	TestFalse(TEXT("No terminal failure at start"), Runtime->HasTerminalFailure());
	TestEqual(
		TEXT("Protect starts Active"),
		Runtime->GetProgress(TEXT("ProtectFriendly")).State,
		ESkyguardMissionObjectiveState::Active);
	TestEqual(
		TEXT("Protect starts at zero progress"),
		Runtime->GetProgress(TEXT("ProtectFriendly")).CurrentProgress,
		0);

	TestTrue(
		TEXT("Destroy progress is accepted while Active"),
		Runtime->AddProgress(TEXT("ClearThreats")));
	TestFalse(
		TEXT("Partial destroy still blocks required completion"),
		Runtime->AreRequiredObjectivesComplete());

	TestTrue(
		TEXT("Protect completes while still Active"),
		Runtime->CompleteSurviveObjectiveIfIntact(TEXT("ProtectFriendly")));
	const FSkyguardObjectiveProgress AfterIntact =
		Runtime->GetProgress(TEXT("ProtectFriendly"));
	TestEqual(
		TEXT("Protect is Completed after intact survive"),
		AfterIntact.State,
		ESkyguardMissionObjectiveState::Completed);
	TestEqual(
		TEXT("Intact survive fills required progress once"),
		AfterIntact.CurrentProgress,
		3);
	TestFalse(
		TEXT("Completed protect cannot complete again"),
		Runtime->CompleteSurviveObjectiveIfIntact(TEXT("ProtectFriendly")));
	TestEqual(
		TEXT("Second intact call does not change progress"),
		Runtime->GetProgress(TEXT("ProtectFriendly")).CurrentProgress,
		3);
	TestFalse(
		TEXT("Completed protect cannot receive AddProgress"),
		Runtime->AddProgress(TEXT("ProtectFriendly")));
	TestFalse(
		TEXT("Required still blocked until destroy completes"),
		Runtime->AreRequiredObjectivesComplete());

	TestTrue(
		TEXT("Second destroy tick completes that objective"),
		Runtime->AddProgress(TEXT("ClearThreats")));
	TestTrue(
		TEXT("Required objectives complete after both succeed"),
		Runtime->AreRequiredObjectivesComplete());
	TestFalse(
		TEXT("Success path has no terminal failure"),
		Runtime->HasTerminalFailure());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardFailedSurviveProtectDoesNotInventProgressTest,
	"Skyguard52.Objectives.Runtime.FailedSurviveProtectDoesNotInventProgress",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardFailedSurviveProtectDoesNotInventProgressTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardObjectiveRuntimeTests;

	USkyguardObjectiveRuntime* Runtime = NewObject<USkyguardObjectiveRuntime>();
	TestNotNull(TEXT("Objective runtime is created"), Runtime);
	if (!Runtime)
	{
		return false;
	}

	const TArray<FSkyguardObjectiveDefinition> Definitions = {
		MakeDestroy(TEXT("ClearThreats"), 1),
		MakeSurviveProtect(
			TEXT("SurviveSortie"),
			ESkyguardMissionObjectiveType::Survive,
			3)
	};
	Runtime->InitializeObjectives(Definitions);

	TestTrue(
		TEXT("Survive can fail while Active"),
		Runtime->FailObjective(TEXT("SurviveSortie")));
	const FSkyguardObjectiveProgress AfterFail =
		Runtime->GetProgress(TEXT("SurviveSortie"));
	TestEqual(
		TEXT("Survive is Failed"),
		AfterFail.State,
		ESkyguardMissionObjectiveState::Failed);
	TestEqual(
		TEXT("Fail does not invent progress"),
		AfterFail.CurrentProgress,
		0);
	TestTrue(
		TEXT("Failure-ending survive is terminal"),
		Runtime->HasTerminalFailure());
	TestFalse(
		TEXT("Failed survive blocks required completion"),
		Runtime->AreRequiredObjectivesComplete());

	TestFalse(
		TEXT("Failed survive cannot complete as intact"),
		Runtime->CompleteSurviveObjectiveIfIntact(TEXT("SurviveSortie")));
	const FSkyguardObjectiveProgress AfterRejectedIntact =
		Runtime->GetProgress(TEXT("SurviveSortie"));
	TestEqual(
		TEXT("Rejected intact leaves Failed state"),
		AfterRejectedIntact.State,
		ESkyguardMissionObjectiveState::Failed);
	TestEqual(
		TEXT("Rejected intact does not invent progress"),
		AfterRejectedIntact.CurrentProgress,
		0);
	TestFalse(
		TEXT("Failed survive cannot receive AddProgress"),
		Runtime->AddProgress(TEXT("SurviveSortie")));
	TestEqual(
		TEXT("Rejected AddProgress does not invent progress"),
		Runtime->GetProgress(TEXT("SurviveSortie")).CurrentProgress,
		0);

	TestTrue(
		TEXT("Destroy still accepts progress"),
		Runtime->AddProgress(TEXT("ClearThreats")));
	TestFalse(
		TEXT("Required stay incomplete after sibling completes"),
		Runtime->AreRequiredObjectivesComplete());
	TestTrue(TEXT("Terminal failure remains"), Runtime->HasTerminalFailure());
	TestFalse(
		TEXT("Already-failed survive cannot fail again"),
		Runtime->FailObjective(TEXT("SurviveSortie")));
	return true;
}

#endif
