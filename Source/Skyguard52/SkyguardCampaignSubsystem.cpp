#include "SkyguardCampaignSubsystem.h"

#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSaveGame.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRouteRuntime.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/Paths.h"

bool USkyguardCampaignSubsystem::ConfigureCampaign(USkyguardCampaignDefinition* InCampaign)
{
	TArray<FText> Errors;
	if (!InCampaign || !InCampaign->ValidateDefinition(Errors))
	{
		return false;
	}
	if (Campaign != InCampaign)
	{
		MissionRecords.Reset();
		LastDebrief = FSkyguardMissionDebrief();
	}
	Campaign = InCampaign;
	ActiveMission = nullptr;
	ObjectiveRuntime = nullptr;
	RouteRuntime = nullptr;
	return true;
}

bool USkyguardCampaignSubsystem::CanStartMission(const FName MissionId) const
{
	return IsMissionUnlocked(MissionId);
}

bool USkyguardCampaignSubsystem::IsMissionUnlocked(const FName MissionId) const
{
	const USkyguardMissionDefinition* Mission =
		Campaign ? Campaign->FindMission(MissionId) : nullptr;
	if (!Mission)
	{
		return false;
	}
	for (const FName PrerequisiteId : Mission->PrerequisiteMissionIds)
	{
		const FSkyguardMissionSaveRecord* Record = MissionRecords.Find(PrerequisiteId);
		if (!Record || !Record->bCompleted)
		{
			return false;
		}
	}
	return GetEarnedCampaignMedals() >= Mission->RequiredCampaignMedals;
}

bool USkyguardCampaignSubsystem::StartMission(const FName MissionId)
{
	USkyguardMissionDefinition* Mission =
		Campaign ? Campaign->FindMission(MissionId) : nullptr;
	if (!Mission || !CanStartMission(MissionId))
	{
		return false;
	}

	USkyguardObjectiveRuntime* NewObjectiveRuntime =
		NewObject<USkyguardObjectiveRuntime>(this);
	USkyguardRouteRuntime* NewRouteRuntime =
		NewObject<USkyguardRouteRuntime>(this);
	if (!NewRouteRuntime->InitializeRoute(Mission->Route))
	{
		return false;
	}

	NewObjectiveRuntime->InitializeObjectives(Mission->Objectives);
	ActiveMission = Mission;
	ObjectiveRuntime = NewObjectiveRuntime;
	RouteRuntime = NewRouteRuntime;
	LastDebrief = FSkyguardMissionDebrief();
	return true;
}

bool USkyguardCampaignSubsystem::AddObjectiveProgress(
	const FName ObjectiveId,
	const int32 Amount)
{
	return ObjectiveRuntime && ObjectiveRuntime->AddProgress(ObjectiveId, Amount);
}

bool USkyguardCampaignSubsystem::FailObjective(const FName ObjectiveId)
{
	return ObjectiveRuntime && ObjectiveRuntime->FailObjective(ObjectiveId);
}

int32 USkyguardCampaignSubsystem::CalculateMissionScore(
	const USkyguardMissionDefinition& Mission,
	const FSkyguardMissionResult& Result)
{
	if (!Result.bMissionSucceeded)
	{
		return 0;
	}

	int32 Score = Mission.ScoreRules.CompletionScore;
	TSet<FName> RewardedObjectives;
	for (const FName ObjectiveId : Result.CompletedObjectiveIds)
	{
		if (RewardedObjectives.Contains(ObjectiveId))
		{
			continue;
		}
		RewardedObjectives.Add(ObjectiveId);
		if (const FSkyguardObjectiveDefinition* Objective = Mission.FindObjective(ObjectiveId))
		{
			Score += Objective->ScoreReward;
		}
	}
	if (Result.ShotsFired > 0 && Result.Hits == Result.ShotsFired)
	{
		Score += Mission.ScoreRules.PerfectAccuracyBonus;
	}
	if (Result.AircraftDamageFraction <= KINDA_SMALL_NUMBER)
	{
		Score += Mission.ScoreRules.NoDamageBonus;
	}
	return FMath::Max(0, Score);
}

int32 USkyguardCampaignSubsystem::CalculateMedalTier(
	const FSkyguardMissionScoreRules& Rules,
	const int32 Score)
{
	if (Score >= Rules.GoldThreshold)
	{
		return 3;
	}
	if (Score >= Rules.SilverThreshold)
	{
		return 2;
	}
	if (Score >= Rules.BronzeThreshold)
	{
		return 1;
	}
	return 0;
}

bool USkyguardCampaignSubsystem::CompleteActiveMission(
	FSkyguardMissionResult& InOutResult)
{
	if (!ActiveMission || !ObjectiveRuntime ||
		ObjectiveRuntime->HasTerminalFailure() ||
		!ObjectiveRuntime->AreRequiredObjectivesComplete())
	{
		return false;
	}

	USkyguardMissionDefinition* CompletedMission = ActiveMission;
	const FSkyguardMissionSaveRecord* ExistingRecord =
		MissionRecords.Find(CompletedMission->MissionId);
	const TOptional<FSkyguardMissionSaveRecord> PreviousRecord =
		ExistingRecord
			? TOptional<FSkyguardMissionSaveRecord>(*ExistingRecord)
			: TOptional<FSkyguardMissionSaveRecord>();

	InOutResult.MissionId = CompletedMission->MissionId;
	InOutResult.bMissionSucceeded = true;
	InOutResult.CompletedObjectiveIds = ObjectiveRuntime->GetCompletedObjectiveIds();
	InOutResult.FinalScore = CalculateMissionScore(*CompletedMission, InOutResult);
	InOutResult.MedalTier =
		CalculateMedalTier(
			CompletedMission->ScoreRules,
			InOutResult.FinalScore);

	FSkyguardMissionSaveRecord& Record =
		MissionRecords.FindOrAdd(CompletedMission->MissionId);
	Record.bCompleted = true;
	Record.BestScore = FMath::Max(Record.BestScore, InOutResult.FinalScore);
	Record.BestMedalTier = FMath::Max(Record.BestMedalTier, InOutResult.MedalTier);
	if (Record.BestCompletionTimeSeconds <= 0.f ||
		(InOutResult.CompletionTimeSeconds > 0.f &&
			InOutResult.CompletionTimeSeconds < Record.BestCompletionTimeSeconds))
	{
		Record.BestCompletionTimeSeconds = InOutResult.CompletionTimeSeconds;
	}

	BuildSuccessDebrief(
		*CompletedMission,
		InOutResult,
		PreviousRecord.IsSet() ? &PreviousRecord.GetValue() : nullptr);
	ActiveMission = nullptr;
	ObjectiveRuntime = nullptr;
	RouteRuntime = nullptr;
	return true;
}

void USkyguardCampaignSubsystem::BuildSuccessDebrief(
	const USkyguardMissionDefinition& CompletedMission,
	const FSkyguardMissionResult& Result,
	const FSkyguardMissionSaveRecord* PreviousRecord)
{
	LastDebrief = FSkyguardMissionDebrief();
	LastDebrief.State = ESkyguardMissionDebriefState::Ready;
	LastDebrief.Result = Result;
	LastDebrief.MissionDisplayName = CompletedMission.DisplayName;
	LastDebrief.Narrative = CompletedMission.Presentation.SuccessDebrief;
	LastDebrief.bNewBestScore =
		!PreviousRecord || Result.FinalScore > PreviousRecord->BestScore;
	LastDebrief.bNewBestMedal =
		!PreviousRecord || Result.MedalTier > PreviousRecord->BestMedalTier;

	USkyguardMissionDefinition* NextMission = nullptr;
	if (Campaign)
	{
		for (USkyguardMissionDefinition* Candidate : Campaign->Missions)
		{
			if (!Candidate ||
				Candidate->CampaignOrder <= CompletedMission.CampaignOrder)
			{
				continue;
			}
			if (!NextMission ||
				Candidate->CampaignOrder < NextMission->CampaignOrder)
			{
				NextMission = Candidate;
			}
		}
	}
	LastDebrief.bCampaignComplete = NextMission == nullptr;
	if (NextMission)
	{
		LastDebrief.NextMissionId = NextMission->MissionId;
		LastDebrief.NextMissionDisplayName = NextMission->DisplayName;
		LastDebrief.NextMissionMap = NextMission->MissionMap;
		LastDebrief.bNextMissionUnlocked =
			IsMissionUnlocked(NextMission->MissionId);
	}
}

bool USkyguardCampaignSubsystem::FinalizeActiveMission(
	FSkyguardMissionResult& InOutResult,
	const FString& SlotName,
	const int32 UserIndex)
{
	if (!CompleteActiveMission(InOutResult))
	{
		return false;
	}
	LastDebrief.SaveSlotName = SlotName;
	LastDebrief.bProgressSaved =
		SaveCampaignToSlot(SlotName, UserIndex);
	return true;
}

bool USkyguardCampaignSubsystem::RetrySaveLastDebrief(
	const FString& SlotName,
	const int32 UserIndex)
{
	if (LastDebrief.State == ESkyguardMissionDebriefState::Unavailable)
	{
		return false;
	}
	LastDebrief.SaveSlotName = SlotName;
	LastDebrief.bProgressSaved =
		SaveCampaignToSlot(SlotName, UserIndex);
	return LastDebrief.bProgressSaved;
}

bool USkyguardCampaignSubsystem::AcknowledgeDebrief()
{
	if (LastDebrief.State != ESkyguardMissionDebriefState::Ready)
	{
		return false;
	}
	LastDebrief.State = ESkyguardMissionDebriefState::Acknowledged;
	return true;
}

FString USkyguardCampaignSubsystem::GetNextMissionMapPackageName() const
{
	if (LastDebrief.NextMissionMap.IsNull())
	{
		return FString();
	}
	return LastDebrief.NextMissionMap.ToSoftObjectPath().GetLongPackageName();
}

bool USkyguardCampaignSubsystem::CanTravelToNextMission() const
{
	return LastDebrief.State ==
			ESkyguardMissionDebriefState::Acknowledged &&
		LastDebrief.bProgressSaved &&
		LastDebrief.bNextMissionUnlocked &&
		!GetNextMissionMapPackageName().IsEmpty();
}

bool USkyguardCampaignSubsystem::TravelToNextMission(
	UObject* WorldContextObject)
{
	if (!WorldContextObject || !CanTravelToNextMission())
	{
		return false;
	}
	UGameplayStatics::OpenLevel(
		WorldContextObject,
		FName(*GetNextMissionMapPackageName()));
	return true;
}

int32 USkyguardCampaignSubsystem::GetEarnedCampaignMedals() const
{
	int32 Total = 0;
	for (const TPair<FName, FSkyguardMissionSaveRecord>& Pair : MissionRecords)
	{
		Total += Pair.Value.BestMedalTier;
	}
	return Total;
}

bool USkyguardCampaignSubsystem::ApplySaveGame(
	const USkyguardCampaignSaveGame* SaveGame)
{
	if (!Campaign || !SaveGame ||
		SaveGame->SaveVersion != USkyguardCampaignSaveGame::CurrentSaveVersion ||
		SaveGame->CampaignId != Campaign->CampaignId)
	{
		return false;
	}

	MissionRecords.Reset();
	for (const TPair<FName, FSkyguardMissionSaveRecord>& Pair : SaveGame->MissionRecords)
	{
		if (Campaign->FindMission(Pair.Key))
		{
			FSkyguardMissionSaveRecord Sanitized = Pair.Value;
			Sanitized.BestScore = FMath::Max(0, Sanitized.BestScore);
			Sanitized.BestMedalTier = FMath::Clamp(Sanitized.BestMedalTier, 0, 3);
			Sanitized.BestCompletionTimeSeconds =
				FMath::IsFinite(Sanitized.BestCompletionTimeSeconds)
					? FMath::Max(0.f, Sanitized.BestCompletionTimeSeconds)
					: 0.f;
			if (!Sanitized.bCompleted)
			{
				Sanitized.BestScore = 0;
				Sanitized.BestMedalTier = 0;
				Sanitized.BestCompletionTimeSeconds = 0.f;
			}
			MissionRecords.Add(Pair.Key, Sanitized);
		}
	}
	ActiveMission = nullptr;
	ObjectiveRuntime = nullptr;
	RouteRuntime = nullptr;
	LastDebrief = FSkyguardMissionDebrief();
	return true;
}

USkyguardCampaignSaveGame* USkyguardCampaignSubsystem::BuildSaveGame() const
{
	if (!Campaign)
	{
		return nullptr;
	}
	USkyguardCampaignSaveGame* SaveGame =
		NewObject<USkyguardCampaignSaveGame>(GetTransientPackage());
	SaveGame->SaveVersion = USkyguardCampaignSaveGame::CurrentSaveVersion;
	SaveGame->CampaignId = Campaign->CampaignId;
	SaveGame->MissionRecords = MissionRecords;
	SaveGame->SavedAtUtc = FDateTime::UtcNow();
	return SaveGame;
}

bool USkyguardCampaignSubsystem::IsValidCampaignSlotName(const FString& SlotName)
{
	const FString Trimmed = SlotName.TrimStartAndEnd();
	return !Trimmed.IsEmpty() &&
		Trimmed == SlotName &&
		Trimmed.Len() <= 64 &&
		FPaths::MakeValidFileName(Trimmed) == Trimmed;
}

bool USkyguardCampaignSubsystem::SaveCampaignToSlot(
	const FString& SlotName,
	const int32 UserIndex) const
{
	if (UserIndex < 0 || !IsValidCampaignSlotName(SlotName))
	{
		return false;
	}
	USkyguardCampaignSaveGame* SaveGame = BuildSaveGame();
	return SaveGame &&
		UGameplayStatics::SaveGameToSlot(SaveGame, SlotName, UserIndex);
}

bool USkyguardCampaignSubsystem::LoadCampaignFromSlot(
	const FString& SlotName,
	const int32 UserIndex)
{
	if (!Campaign || UserIndex < 0 || !IsValidCampaignSlotName(SlotName) ||
		!UGameplayStatics::DoesSaveGameExist(SlotName, UserIndex))
	{
		return false;
	}
	USaveGame* Loaded = UGameplayStatics::LoadGameFromSlot(SlotName, UserIndex);
	return ApplySaveGame(Cast<USkyguardCampaignSaveGame>(Loaded));
}

bool USkyguardCampaignSubsystem::DeleteCampaignSlot(
	const FString& SlotName,
	const int32 UserIndex) const
{
	if (UserIndex < 0 || !IsValidCampaignSlotName(SlotName))
	{
		return false;
	}
	return !UGameplayStatics::DoesSaveGameExist(SlotName, UserIndex) ||
		UGameplayStatics::DeleteGameInSlot(SlotName, UserIndex);
}
