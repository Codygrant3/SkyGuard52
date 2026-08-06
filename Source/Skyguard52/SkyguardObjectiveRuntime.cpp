#include "SkyguardObjectiveRuntime.h"

void USkyguardObjectiveRuntime::InitializeObjectives(
	const TArray<FSkyguardObjectiveDefinition>& Definitions)
{
	AuthoredDefinitions = Definitions;
	RuntimeProgress.Reset();
	for (const FSkyguardObjectiveDefinition& Definition : Definitions)
	{
		FSkyguardObjectiveProgress Progress;
		Progress.ObjectiveId = Definition.ObjectiveId;
		Progress.State = ESkyguardMissionObjectiveState::Active;
		RuntimeProgress.Add(Definition.ObjectiveId, Progress);
	}
}

bool USkyguardObjectiveRuntime::AddProgress(const FName ObjectiveId, const int32 Amount)
{
	FSkyguardObjectiveProgress* Progress = RuntimeProgress.Find(ObjectiveId);
	const FSkyguardObjectiveDefinition* Definition = AuthoredDefinitions.FindByPredicate(
		[ObjectiveId](const FSkyguardObjectiveDefinition& Candidate)
		{
			return Candidate.ObjectiveId == ObjectiveId;
		});
	if (!Progress || !Definition || Amount <= 0 ||
		Progress->State != ESkyguardMissionObjectiveState::Active)
	{
		return false;
	}

	Progress->CurrentProgress =
		FMath::Min(Progress->CurrentProgress + Amount, Definition->RequiredProgress);
	if (Progress->CurrentProgress >= Definition->RequiredProgress)
	{
		Progress->State = ESkyguardMissionObjectiveState::Completed;
	}
	return true;
}

bool USkyguardObjectiveRuntime::FailObjective(const FName ObjectiveId)
{
	FSkyguardObjectiveProgress* Progress = RuntimeProgress.Find(ObjectiveId);
	if (!Progress || Progress->State != ESkyguardMissionObjectiveState::Active)
	{
		return false;
	}
	Progress->State = ESkyguardMissionObjectiveState::Failed;
	return true;
}

bool USkyguardObjectiveRuntime::AreRequiredObjectivesComplete() const
{
	for (const FSkyguardObjectiveDefinition& Definition : AuthoredDefinitions)
	{
		if (!Definition.bRequiredForMissionSuccess)
		{
			continue;
		}
		const FSkyguardObjectiveProgress* Progress = RuntimeProgress.Find(Definition.ObjectiveId);
		if (!Progress || Progress->State != ESkyguardMissionObjectiveState::Completed)
		{
			return false;
		}
	}
	return !AuthoredDefinitions.IsEmpty();
}

bool USkyguardObjectiveRuntime::HasTerminalFailure() const
{
	for (const FSkyguardObjectiveDefinition& Definition : AuthoredDefinitions)
	{
		const FSkyguardObjectiveProgress* Progress = RuntimeProgress.Find(Definition.ObjectiveId);
		if (Definition.bFailureEndsMission && Progress &&
			Progress->State == ESkyguardMissionObjectiveState::Failed)
		{
			return true;
		}
	}
	return false;
}

FSkyguardObjectiveProgress USkyguardObjectiveRuntime::GetProgress(const FName ObjectiveId) const
{
	if (const FSkyguardObjectiveProgress* Progress = RuntimeProgress.Find(ObjectiveId))
	{
		return *Progress;
	}
	return FSkyguardObjectiveProgress();
}

TArray<FName> USkyguardObjectiveRuntime::GetCompletedObjectiveIds() const
{
	TArray<FName> Completed;
	for (const TPair<FName, FSkyguardObjectiveProgress>& Pair : RuntimeProgress)
	{
		if (Pair.Value.State == ESkyguardMissionObjectiveState::Completed)
		{
			Completed.Add(Pair.Key);
		}
	}
	Completed.Sort(FNameLexicalLess());
	return Completed;
}
