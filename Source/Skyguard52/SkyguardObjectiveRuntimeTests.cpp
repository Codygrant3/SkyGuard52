#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardObjectiveRuntime.h"

#include "Misc/AutomationTest.h"

namespace SkyguardObjectiveRuntimeTests
{
	FSkyguardObjectiveDefinition MakeObjective(
		const FName ObjectiveId,
		const ESkyguardMissionObjectiveType Type,
		const int32 RequiredProgress,
		const bool bRequiredForMissionSuccess,
		const bool bFailureEndsMission)
	{
		FSkyguardObjectiveDefinition Definition;
		Definition.ObjectiveId = ObjectiveId;
		Definition.DisplayName = FText::FromName(ObjectiveId);
		Definition.Type = Type;
		Definition.RequiredProgress = RequiredProgress;
		Definition.bRequiredForMissionSuccess = bRequiredForMissionSuccess;
		Definition.bFailureEndsMission = bFailureEndsMission;
		return Definition;
	}

	USkyguardObjectiveRuntime* MakeRuntime(
		const TArray<FSkyguardObjectiveDefinition>& Definitions)
	{
		USkyguardObjectiveRuntime* Runtime = NewObject<USkyguardObjectiveRuntime>();
		if (Runtime)
		{
			Runtime->InitializeObjectives(Definitions);
		}
		return Runtime;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSurviveObjectiveCompletesOnlyWhileActiveTest,
	"Skyguard52.Campaign.Runtime.SurviveObjectiveCompletesOnlyWhileActive",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSurviveObjectiveCompletesOnlyWhileActiveTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardObjectiveRuntimeTests;

	const FName SurviveId = TEXT("HoldTheLine");
	const FName DestroyId = TEXT("ClearTheRidge");
	USkyguardObjectiveRuntime* Runtime = MakeRuntime({
		MakeObjective(
			SurviveId,
			ESkyguardMissionObjectiveType::Survive,
			1,
			true,
			true),
		MakeObjective(
			DestroyId,
			ESkyguardMissionObjectiveType::DestroyTargets,
			2,
			true,
			false)
	});
	TestNotNull(TEXT("Objective runtime is created"), Runtime);
	if (!Runtime)
	{
		return false;
	}

	const FSkyguardObjectiveProgress SurviveStart = Runtime->GetProgress(SurviveId);
	TestEqual(TEXT("Survive starts Active"), SurviveStart.State, ESkyguardMissionObjectiveState::Active);
	TestEqual(TEXT("Survive starts at zero progress"), SurviveStart.CurrentProgress, 0);
	TestFalse(TEXT("Required objectives start incomplete"), Runtime->AreRequiredObjectivesComplete());
	TestFalse(TEXT("No terminal failure at start"), Runtime->HasTerminalFailure());

	TestTrue(TEXT("Destroy progress is accepted while Active"), Runtime->AddProgress(DestroyId, 1));
	TestFalse(
		TEXT("Partial destroy progress still blocks required completion"),
		Runtime->AreRequiredObjectivesComplete());
	TestEqual(
		TEXT("Partial destroy progress is recorded"),
		Runtime->GetProgress(DestroyId).CurrentProgress,
		1);

	TestTrue(
		TEXT("Intact survive completes while Active"),
		Runtime->CompleteSurviveObjectiveIfIntact(SurviveId));
	const FSkyguardObjectiveProgress SurviveDone = Runtime->GetProgress(SurviveId);
	TestEqual(
		TEXT("Intact survive becomes Completed"),
		SurviveDone.State,
		ESkyguardMissionObjectiveState::Completed);
	TestEqual(
		TEXT("Intact survive fills authored required progress"),
		SurviveDone.CurrentProgress,
		1);
	TestFalse(
		TEXT("Survive complete alone does not finish required set"),
		Runtime->AreRequiredObjectivesComplete());
	TestFalse(TEXT("Intact survive complete is not a terminal failure"), Runtime->HasTerminalFailure());

	TestFalse(
		TEXT("Completed survive cannot complete again"),
		Runtime->CompleteSurviveObjectiveIfIntact(SurviveId));
	TestEqual(
		TEXT("Second intact complete does not change progress"),
		Runtime->GetProgress(SurviveId).CurrentProgress,
		1);
	TestFalse(TEXT("Completed survive cannot fail"), Runtime->FailObjective(SurviveId));
	TestFalse(TEXT("Completed survive rejects AddProgress"), Runtime->AddProgress(SurviveId, 1));

	TestTrue(TEXT("Final destroy progress completes the required set"), Runtime->AddProgress(DestroyId, 1));
	TestTrue(TEXT("Required objectives complete after both succeed"), Runtime->AreRequiredObjectivesComplete());
	TestFalse(TEXT("Successful required set has no terminal failure"), Runtime->HasTerminalFailure());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardFailThenSurviveCompleteDoesNotInventProgressTest,
	"Skyguard52.Campaign.Runtime.FailThenSurviveCompleteDoesNotInventProgress",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardFailThenSurviveCompleteDoesNotInventProgressTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardObjectiveRuntimeTests;

	const FName SurviveId = TEXT("HoldTheLine");
	const FName DestroyId = TEXT("ClearTheRidge");
	USkyguardObjectiveRuntime* Runtime = MakeRuntime({
		MakeObjective(
			SurviveId,
			ESkyguardMissionObjectiveType::Survive,
			3,
			true,
			true),
		MakeObjective(
			DestroyId,
			ESkyguardMissionObjectiveType::DestroyTargets,
			1,
			true,
			false)
	});
	TestNotNull(TEXT("Objective runtime is created"), Runtime);
	if (!Runtime)
	{
		return false;
	}

	TestTrue(TEXT("Partial survive AddProgress is accepted while Active"), Runtime->AddProgress(SurviveId, 1));
	TestEqual(
		TEXT("Partial survive progress stays below required"),
		Runtime->GetProgress(SurviveId).CurrentProgress,
		1);
	TestEqual(
		TEXT("Partial survive remains Active"),
		Runtime->GetProgress(SurviveId).State,
		ESkyguardMissionObjectiveState::Active);
	TestFalse(TEXT("Partial survive is not required-complete"), Runtime->AreRequiredObjectivesComplete());
	TestFalse(TEXT("Partial survive is not a terminal failure"), Runtime->HasTerminalFailure());

	TestTrue(TEXT("Active survive can fail"), Runtime->FailObjective(SurviveId));
	const FSkyguardObjectiveProgress AfterFail = Runtime->GetProgress(SurviveId);
	TestEqual(TEXT("Failed survive is Failed"), AfterFail.State, ESkyguardMissionObjectiveState::Failed);
	TestEqual(TEXT("FailObjective does not invent progress"), AfterFail.CurrentProgress, 1);
	TestTrue(TEXT("Failure-ending survive is terminal"), Runtime->HasTerminalFailure());
	TestFalse(TEXT("Failed required survive blocks success"), Runtime->AreRequiredObjectivesComplete());

	TestFalse(
		TEXT("Failed survive cannot complete as intact"),
		Runtime->CompleteSurviveObjectiveIfIntact(SurviveId));
	const FSkyguardObjectiveProgress AfterBogusComplete = Runtime->GetProgress(SurviveId);
	TestEqual(
		TEXT("Failed survive stays Failed after intact complete"),
		AfterBogusComplete.State,
		ESkyguardMissionObjectiveState::Failed);
	TestEqual(
		TEXT("Intact complete after fail does not invent required progress"),
		AfterBogusComplete.CurrentProgress,
		1);
	TestFalse(TEXT("Failed survive rejects further AddProgress"), Runtime->AddProgress(SurviveId, 2));
	TestEqual(
		TEXT("Rejected AddProgress does not invent progress"),
		Runtime->GetProgress(SurviveId).CurrentProgress,
		1);
	TestFalse(TEXT("Failed survive cannot fail again"), Runtime->FailObjective(SurviveId));
	TestTrue(TEXT("Destroy can still accept progress after survive failed"), Runtime->AddProgress(DestroyId, 1));
	TestFalse(
		TEXT("Completed destroy cannot rescue a failed required survive"),
		Runtime->AreRequiredObjectivesComplete());
	TestTrue(TEXT("Terminal failure remains after destroy completes"), Runtime->HasTerminalFailure());

	TestFalse(
		TEXT("Unknown id does not complete as intact"),
		Runtime->CompleteSurviveObjectiveIfIntact(TEXT("MissingObjective")));
	TestFalse(TEXT("Unknown id cannot fail"), Runtime->FailObjective(TEXT("MissingObjective")));
	TestFalse(TEXT("Unknown id rejects AddProgress"), Runtime->AddProgress(TEXT("MissingObjective"), 1));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardProtectAssetIntactContractTest,
	"Skyguard52.Campaign.Runtime.ProtectAssetCompletesOnlyWhileActive",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardProtectAssetIntactContractTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardObjectiveRuntimeTests;

	const FName ProtectId = TEXT("GuardTheConvoy");
	const FName DestroyId = TEXT("ClearTheRidge");
	USkyguardObjectiveRuntime* Intact = MakeRuntime({
		MakeObjective(
			ProtectId,
			ESkyguardMissionObjectiveType::ProtectAsset,
			1,
			true,
			true),
		MakeObjective(
			DestroyId,
			ESkyguardMissionObjectiveType::DestroyTargets,
			1,
			true,
			false)
	});
	TestNotNull(TEXT("Intact protect runtime is created"), Intact);
	if (!Intact)
	{
		return false;
	}

	TestFalse(TEXT("Protect starts incomplete"), Intact->AreRequiredObjectivesComplete());
	TestTrue(
		TEXT("Intact protect completes while Active"),
		Intact->CompleteSurviveObjectiveIfIntact(ProtectId));
	TestEqual(
		TEXT("Intact protect becomes Completed"),
		Intact->GetProgress(ProtectId).State,
		ESkyguardMissionObjectiveState::Completed);
	TestEqual(
		TEXT("Intact protect fills required progress"),
		Intact->GetProgress(ProtectId).CurrentProgress,
		1);
	TestTrue(TEXT("Destroy progress completes the required set"), Intact->AddProgress(DestroyId, 1));
	TestTrue(TEXT("Required objectives complete when protect stays intact"), Intact->AreRequiredObjectivesComplete());
	TestFalse(TEXT("Intact protect is not a terminal failure"), Intact->HasTerminalFailure());
	TestFalse(
		TEXT("Completed protect cannot complete again"),
		Intact->CompleteSurviveObjectiveIfIntact(ProtectId));

	USkyguardObjectiveRuntime* Broken = MakeRuntime({
		MakeObjective(
			ProtectId,
			ESkyguardMissionObjectiveType::ProtectAsset,
			4,
			true,
			true),
		MakeObjective(
			DestroyId,
			ESkyguardMissionObjectiveType::DestroyTargets,
			1,
			true,
			false)
	});
	TestNotNull(TEXT("Broken protect runtime is created"), Broken);
	if (!Broken)
	{
		return false;
	}

	TestTrue(TEXT("Partial protect AddProgress is accepted"), Broken->AddProgress(ProtectId, 1));
	TestTrue(TEXT("Active protect can fail"), Broken->FailObjective(ProtectId));
	TestEqual(
		TEXT("Failed protect keeps partial progress"),
		Broken->GetProgress(ProtectId).CurrentProgress,
		1);
	TestTrue(TEXT("Failed protect is terminal"), Broken->HasTerminalFailure());
	TestFalse(
		TEXT("Failed protect cannot complete as intact"),
		Broken->CompleteSurviveObjectiveIfIntact(ProtectId));
	TestEqual(
		TEXT("Intact complete after protect fail does not invent progress"),
		Broken->GetProgress(ProtectId).CurrentProgress,
		1);
	TestEqual(
		TEXT("Failed protect stays Failed"),
		Broken->GetProgress(ProtectId).State,
		ESkyguardMissionObjectiveState::Failed);
	TestFalse(TEXT("Failed required protect blocks success"), Broken->AreRequiredObjectivesComplete());
	return true;
}

#endif
