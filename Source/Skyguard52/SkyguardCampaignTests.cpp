#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSaveGame.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRouteRuntime.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/AutomationTest.h"

namespace SkyguardCampaignTests
{
	USkyguardMissionDefinition* MakeMission(
		const FName MissionId,
		const int32 CampaignOrder)
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>(GetTransientPackage());
		Mission->MissionId = MissionId;
		Mission->DisplayName = FText::FromName(MissionId);
		Mission->CampaignOrder = CampaignOrder;
		Mission->MissionMap = TSoftObjectPtr<UWorld>(
			FSoftObjectPath(FString::Printf(
				TEXT("/Game/Skyguard/Maps/Automation/Lvl_%s.Lvl_%s"),
				*MissionId.ToString(),
				*MissionId.ToString())));
		Mission->Route.RouteId = FName(*FString::Printf(TEXT("%s_Route"), *MissionId.ToString()));

		FSkyguardRoutePoint Start;
		Start.PointId = TEXT("Start");
		Start.WorldLocation = FVector::ZeroVector;
		FSkyguardRoutePoint Mid;
		Mid.PointId = TEXT("Mid");
		Mid.WorldLocation = FVector(1000.f, 0.f, 0.f);
		FSkyguardRoutePoint End;
		End.PointId = TEXT("End");
		End.WorldLocation = FVector(1000.f, 1000.f, 0.f);
		Mission->Route.Points = { Start, Mid, End };

		FSkyguardObjectiveDefinition Required;
		Required.ObjectiveId = TEXT("BossDefeated");
		Required.DisplayName = FText::FromString(TEXT("Defeat the boss"));
		Required.Type = ESkyguardMissionObjectiveType::BossPhase;
		Required.RequiredProgress = 2;
		Required.bRequiredForMissionSuccess = true;
		Required.bFailureEndsMission = false;
		Required.ScoreReward = 1000;

		FSkyguardObjectiveDefinition Optional;
		Optional.ObjectiveId = TEXT("ProtectCity");
		Optional.DisplayName = FText::FromString(TEXT("Protect the city"));
		Optional.Type = ESkyguardMissionObjectiveType::ProtectAsset;
		Optional.bRequiredForMissionSuccess = false;
		Optional.bFailureEndsMission = true;
		Optional.ScoreReward = 500;
		Mission->Objectives = { Required, Optional };

		FSkyguardEnemyFormationDefinition Formation;
		Formation.FormationId = TEXT("EscortVee");
		Formation.UnitCount = 2;
		FSkyguardEnemyWaveDefinition Wave;
		Wave.WaveId = TEXT("OpeningWave");
		Wave.Formations.Add(Formation);
		Wave.CompletionObjectiveId = TEXT("BossDefeated");
		Mission->Waves.Add(Wave);

		Mission->Boss.BossId = FName(*FString::Printf(TEXT("%s_Boss"), *MissionId.ToString()));
		Mission->Boss.Callsign = FText::FromString(TEXT("Pathfinder"));
		Mission->Boss.DefeatObjectiveId = TEXT("BossDefeated");
		FSkyguardBossWeakPointDefinition Antenna;
		Antenna.WeakPointId = TEXT("Antenna");
		Antenna.RequiredWeapon = TEXT("Rifle");
		Antenna.ExposesWeakPointId = TEXT("Engine");
		FSkyguardBossWeakPointDefinition Engine;
		Engine.WeakPointId = TEXT("Engine");
		Engine.RequiredWeapon = TEXT("Igla");
		Mission->Boss.WeakPoints = { Antenna, Engine };

		Mission->Weather.ProfileId = TEXT("ClearNoon");
		Mission->Presentation.Briefing = FText::FromString(TEXT("Defend the coast."));
		Mission->Presentation.SuccessDebrief =
			FText::FromString(TEXT("Coast secured. Return to base."));
		Mission->Presentation.FailureDebrief =
			FText::FromString(TEXT("Coastal defense failed."));
		Mission->ScoreRules.BronzeThreshold = 5000;
		Mission->ScoreRules.SilverThreshold = 8000;
		Mission->ScoreRules.GoldThreshold = 11000;
		return Mission;
	}

	USkyguardCampaignDefinition* MakeTwoMissionCampaign()
	{
		USkyguardCampaignDefinition* Campaign =
			NewObject<USkyguardCampaignDefinition>(GetTransientPackage());
		Campaign->CampaignId = TEXT("AutomationCampaign");
		Campaign->DisplayName = FText::FromString(TEXT("Automation Campaign"));
		USkyguardMissionDefinition* Mission01 = MakeMission(TEXT("M01"), 1);
		USkyguardMissionDefinition* Mission02 = MakeMission(TEXT("M02"), 2);
		Mission02->PrerequisiteMissionIds.Add(TEXT("M01"));
		Mission02->RequiredCampaignMedals = 2;
		Campaign->Missions = { Mission01, Mission02 };
		return Campaign;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionDefinitionValidationTest,
	"Skyguard52.Campaign.Definition.ValidationRejectsBrokenReferences",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionDefinitionValidationTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCampaignTests;

	USkyguardMissionDefinition* Mission = MakeMission(TEXT("M01"), 1);
	TArray<FText> Errors;
	TestTrue(TEXT("A complete mission definition validates"), Mission->ValidateDefinition(Errors));
	TestEqual(TEXT("Valid mission has no validation errors"), Errors.Num(), 0);
	TestEqual(
		TEXT("Mission primary asset id uses stable authored identity"),
		Mission->GetPrimaryAssetId(),
		FPrimaryAssetId(TEXT("SkyguardMission"), TEXT("M01")));

	Mission->Waves[0].CompletionObjectiveId = TEXT("MissingObjective");
	Mission->Boss.WeakPoints[0].ExposesWeakPointId = TEXT("MissingWeakPoint");
	TestFalse(TEXT("Broken objective and weak-point references are rejected"), Mission->ValidateDefinition(Errors));
	TestTrue(TEXT("Validation reports both independent broken references"), Errors.Num() >= 2);

	USkyguardCampaignDefinition* Campaign = MakeTwoMissionCampaign();
	TestTrue(TEXT("Ordered campaign and prerequisites validate"), Campaign->ValidateDefinition(Errors));
	Campaign->Missions[0]->PrerequisiteMissionIds.Add(TEXT("M02"));
	TestFalse(TEXT("Forward/cyclic prerequisites are rejected"), Campaign->ValidateDefinition(Errors));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardObjectiveAndRouteRuntimeTest,
	"Skyguard52.Campaign.Runtime.ObjectivesAndRouteAreDeterministic",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardObjectiveAndRouteRuntimeTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCampaignTests;

	USkyguardMissionDefinition* Mission = MakeMission(TEXT("M01"), 1);
	USkyguardRouteRuntime* Route = NewObject<USkyguardRouteRuntime>();
	TestTrue(TEXT("Three-point route initializes"), Route->InitializeRoute(Mission->Route));
	TestEqual(TEXT("Route length is the sum of both segments"), Route->GetRouteLength(), 2000.f);
	TestTrue(
		TEXT("Distance sampling interpolates inside the second segment"),
		Route->SampleLocationByDistance(1500.f).Equals(FVector(1000.f, 500.f, 0.f), 0.01f));
	TestTrue(
		TEXT("Distance sampling clamps beyond route end"),
		Route->SampleLocationByDistance(9999.f).Equals(FVector(1000.f, 1000.f, 0.f), 0.01f));

	USkyguardObjectiveRuntime* Objectives = NewObject<USkyguardObjectiveRuntime>();
	Objectives->InitializeObjectives(Mission->Objectives);
	TestFalse(TEXT("Required objective initially blocks success"), Objectives->AreRequiredObjectivesComplete());
	TestTrue(TEXT("First boss phase advances progress"), Objectives->AddProgress(TEXT("BossDefeated")));
	TestFalse(TEXT("Partial required progress still blocks success"), Objectives->AreRequiredObjectivesComplete());
	TestTrue(TEXT("Second boss phase completes objective"), Objectives->AddProgress(TEXT("BossDefeated")));
	TestTrue(TEXT("Required objective completion enables success"), Objectives->AreRequiredObjectivesComplete());
	TestFalse(TEXT("Completed objective cannot receive duplicate progress"), Objectives->AddProgress(TEXT("BossDefeated")));
	TestTrue(TEXT("Protected objective can fail"), Objectives->FailObjective(TEXT("ProtectCity")));
	TestTrue(TEXT("Failure-ending objective becomes terminal"), Objectives->HasTerminalFailure());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignProgressionAndSaveTest,
	"Skyguard52.Campaign.Runtime.ScoringUnlocksAndSaveRoundTrip",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignProgressionAndSaveTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCampaignTests;

	USkyguardCampaignDefinition* Campaign = MakeTwoMissionCampaign();
	UGameInstance* GameInstance = NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Runtime =
		NewObject<USkyguardCampaignSubsystem>(GameInstance);
	TestTrue(TEXT("Valid campaign configures runtime"), Runtime->ConfigureCampaign(Campaign));
	TestTrue(TEXT("First mission starts unlocked"), Runtime->CanStartMission(TEXT("M01")));
	TestFalse(TEXT("Second mission starts locked"), Runtime->CanStartMission(TEXT("M02")));
	TestTrue(TEXT("First mission starts"), Runtime->StartMission(TEXT("M01")));
	TestTrue(TEXT("First required progress is accepted"), Runtime->AddObjectiveProgress(TEXT("BossDefeated")));
	TestTrue(TEXT("Second required progress is accepted"), Runtime->AddObjectiveProgress(TEXT("BossDefeated")));

	FSkyguardMissionResult Result;
	Result.ShotsFired = 10;
	Result.Hits = 10;
	Result.AircraftDamageFraction = 0.f;
	Result.CompletionTimeSeconds = 420.f;
	TestTrue(TEXT("Completed required objectives finalize mission"), Runtime->CompleteActiveMission(Result));
	TestEqual(TEXT("Objective, accuracy and no-damage bonuses score deterministically"), Result.FinalScore, 10000);
	TestEqual(TEXT("Ten thousand points awards silver"), Result.MedalTier, 2);
	TestEqual(TEXT("Earned medal total comes from best mission records"), Runtime->GetEarnedCampaignMedals(), 2);
	TestTrue(TEXT("Prerequisite plus medal threshold unlocks Mission 2"), Runtime->CanStartMission(TEXT("M02")));

	FSkyguardMissionResult DuplicateRewardResult = Result;
	DuplicateRewardResult.CompletedObjectiveIds = {
		TEXT("BossDefeated"),
		TEXT("BossDefeated")
	};
	TestEqual(
		TEXT("Duplicate objective ids cannot multiply score rewards"),
		USkyguardCampaignSubsystem::CalculateMissionScore(
			*Campaign->FindMission(TEXT("M01")),
			DuplicateRewardResult),
		10000);

	USkyguardCampaignSaveGame* Save = Runtime->BuildSaveGame();
	TestNotNull(TEXT("Configured campaign builds a save contract"), Save);
	TestEqual(TEXT("Save contract binds to campaign identity"), Save->CampaignId, Campaign->CampaignId);

	UGameInstance* RestoredGameInstance = NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* RestoredRuntime =
		NewObject<USkyguardCampaignSubsystem>(RestoredGameInstance);
	TestTrue(TEXT("Fresh runtime configures same campaign"), RestoredRuntime->ConfigureCampaign(Campaign));
	TestTrue(TEXT("Matching version and campaign save applies"), RestoredRuntime->ApplySaveGame(Save));
	TestTrue(TEXT("Unlock survives save-state round trip"), RestoredRuntime->CanStartMission(TEXT("M02")));
	TestEqual(TEXT("Best medal survives save-state round trip"), RestoredRuntime->GetEarnedCampaignMedals(), 2);

	Save->MissionRecords[TEXT("M01")].BestMedalTier = 99;
	Save->MissionRecords[TEXT("M01")].BestScore = -500;
	Save->MissionRecords[TEXT("M01")].BestCompletionTimeSeconds = -20.f;
	TestTrue(TEXT("Matching save with out-of-range values applies safely"), RestoredRuntime->ApplySaveGame(Save));
	const FSkyguardMissionSaveRecord& SanitizedRecord =
		RestoredRuntime->GetMissionRecords().FindChecked(TEXT("M01"));
	TestEqual(TEXT("Imported medal tier is clamped"), SanitizedRecord.BestMedalTier, 3);
	TestEqual(TEXT("Imported score cannot be negative"), SanitizedRecord.BestScore, 0);
	TestEqual(TEXT("Imported completion time cannot be negative"), SanitizedRecord.BestCompletionTimeSeconds, 0.f);

	Save->CampaignId = TEXT("WrongCampaign");
	TestFalse(TEXT("Cross-campaign save data is rejected"), RestoredRuntime->ApplySaveGame(Save));

	Save->CampaignId = Campaign->CampaignId;
	Save->SaveVersion = USkyguardCampaignSaveGame::CurrentSaveVersion - 1;
	TestTrue(
		TEXT("Legacy save versions migrate forward to current"),
		RestoredRuntime->ApplySaveGame(Save));
	TestTrue(TEXT("Migrated legacy save still unlocks next mission"), RestoredRuntime->CanStartMission(TEXT("M02")));
	// ApplySaveGame migrates a working copy; assert the in-place migrator advances version too.
	TestTrue(
		TEXT("MigrateCampaignSave accepts supported legacy version"),
		USkyguardCampaignSaveGame::MigrateCampaignSave(*Save));
	TestEqual(
		TEXT("Migrated SaveVersion becomes Current"),
		Save->SaveVersion,
		USkyguardCampaignSaveGame::CurrentSaveVersion);

	Save->SaveVersion = USkyguardCampaignSaveGame::CurrentSaveVersion + 1;
	TestFalse(TEXT("Future save versions are rejected"), RestoredRuntime->ApplySaveGame(Save));
	TestFalse(
		TEXT("MigrateCampaignSave rejects future versions"),
		USkyguardCampaignSaveGame::MigrateCampaignSave(*Save));

	Save->SaveVersion = USkyguardCampaignSaveGame::MinSupportedSaveVersion - 1;
	TestFalse(TEXT("Pre-min save versions are rejected"), RestoredRuntime->ApplySaveGame(Save));
	TestFalse(
		TEXT("MigrateCampaignSave rejects pre-min versions"),
		USkyguardCampaignSaveGame::MigrateCampaignSave(*Save));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignSortieDebriefFlowTest,
	"Skyguard52.Campaign.Sortie.BriefingToDebriefSaveAndTravelContract",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignSortieDebriefFlowTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardCampaignTests;

	const FString SlotName = FString::Printf(
		TEXT("SkyguardSortieFlow_%s"),
		*FGuid::NewGuid().ToString(EGuidFormats::Digits));
	USkyguardCampaignDefinition* Campaign = MakeTwoMissionCampaign();
	UGameInstance* GameInstance =
		NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Runtime =
		NewObject<USkyguardCampaignSubsystem>(GameInstance);
	Runtime->DeleteCampaignSlot(SlotName, 0);

	TestTrue(TEXT("Campaign configures"), Runtime->ConfigureCampaign(Campaign));
	USkyguardMissionBriefingComponent* Briefing =
		NewObject<USkyguardMissionBriefingComponent>(GetTransientPackage());
	TestTrue(TEXT("Mission 1 briefing configures"),
		Briefing->ConfigureFromMission(Campaign->FindMission(TEXT("M01"))));
	TestFalse(TEXT("Sortie is blocked while the briefing warms"),
		Briefing->CanLaunch());
	Briefing->SetAssetsReady(true);
	Briefing->AdvanceBriefing(Briefing->GetMinimumWarmupSeconds());
	TestTrue(TEXT("Briefing becomes launch-ready"),
		Briefing->CanLaunch());
	TestTrue(TEXT("Player acknowledges the briefing"),
		Briefing->AcknowledgeAndLaunch());
	TestTrue(TEXT("Mission 1 starts"), Runtime->StartMission(TEXT("M01")));
	TestTrue(TEXT("First required objective step applies"),
		Runtime->AddObjectiveProgress(TEXT("BossDefeated")));
	TestTrue(TEXT("Second required objective step applies"),
		Runtime->AddObjectiveProgress(TEXT("BossDefeated")));

	FSkyguardMissionResult Result;
	Result.ShotsFired = 8;
	Result.Hits = 8;
	Result.AircraftDamageFraction = 0.f;
	Result.CompletionTimeSeconds = 360.f;
	TestTrue(TEXT("Playable sortie finalizes"),
		Runtime->FinalizeActiveMission(Result, SlotName, 0));

	const FSkyguardMissionDebrief& Debrief = Runtime->GetLastDebrief();
	TestEqual(TEXT("Debrief is ready for presentation"),
		Debrief.State, ESkyguardMissionDebriefState::Ready);
	TestEqual(TEXT("Debrief binds the completed mission"),
		Debrief.Result.MissionId, FName(TEXT("M01")));
	TestTrue(TEXT("Debrief uses authored success copy"),
		Debrief.Narrative.EqualTo(
			FText::FromString(TEXT("Coast secured. Return to base."))));
	TestEqual(TEXT("Debrief exposes deterministic score"),
		Debrief.Result.FinalScore, 10000);
	TestEqual(TEXT("Debrief exposes earned medal"),
		Debrief.Result.MedalTier, 2);
	TestTrue(TEXT("First completion is a new best score"),
		Debrief.bNewBestScore);
	TestTrue(TEXT("First completion is a new best medal"),
		Debrief.bNewBestMedal);
	TestTrue(TEXT("Sortie progression persists before travel"),
		Debrief.bProgressSaved);
	TestEqual(TEXT("Next mission is selected in campaign order"),
		Debrief.NextMissionId, FName(TEXT("M02")));
	TestTrue(TEXT("Scored completion unlocks the next mission"),
		Debrief.bNextMissionUnlocked);
	TestEqual(TEXT("Next playable map package is resolved"),
		Runtime->GetNextMissionMapPackageName(),
		FString(TEXT("/Game/Skyguard/Maps/Automation/Lvl_M02")));
	TestFalse(TEXT("Travel remains gated until debrief acknowledgment"),
		Runtime->CanTravelToNextMission());
	TestTrue(TEXT("Player can acknowledge the ready debrief"),
		Runtime->AcknowledgeDebrief());
	TestTrue(TEXT("Saved, unlocked next mission becomes travel-ready"),
		Runtime->CanTravelToNextMission());
	TestFalse(TEXT("Debrief acknowledgment is one-shot"),
		Runtime->AcknowledgeDebrief());

	UGameInstance* RestoredGameInstance =
		NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Restored =
		NewObject<USkyguardCampaignSubsystem>(RestoredGameInstance);
	TestTrue(TEXT("Restored runtime configures"),
		Restored->ConfigureCampaign(Campaign));
	TestTrue(TEXT("Sortie save loads in a fresh runtime"),
		Restored->LoadCampaignFromSlot(SlotName, 0));
	TestTrue(TEXT("Next mission unlock survives persistence"),
		Restored->CanStartMission(TEXT("M02")));
	TestTrue(TEXT("Unique sortie slot is cleaned up"),
		Restored->DeleteCampaignSlot(SlotName, 0));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignDiskPersistenceTest,
	"Skyguard52.Campaign.Persistence.DiskSlotRoundTripAndSanitization",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignDiskPersistenceTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCampaignTests;

	const FString SlotName = FString::Printf(
		TEXT("SkyguardAutomation_%s"),
		*FGuid::NewGuid().ToString(EGuidFormats::Digits));
	constexpr int32 UserIndex = 0;
	USkyguardCampaignDefinition* Campaign = MakeTwoMissionCampaign();
	UGameInstance* SourceGameInstance = NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Source =
		NewObject<USkyguardCampaignSubsystem>(SourceGameInstance);
	TestTrue(TEXT("Source campaign configures"), Source->ConfigureCampaign(Campaign));
	TestTrue(TEXT("Mission 1 starts"), Source->StartMission(TEXT("M01")));
	TestTrue(TEXT("Required objective progress one applies"), Source->AddObjectiveProgress(TEXT("BossDefeated")));
	TestTrue(TEXT("Required objective progress two applies"), Source->AddObjectiveProgress(TEXT("BossDefeated")));

	FSkyguardMissionResult Result;
	Result.ShotsFired = 4;
	Result.Hits = 4;
	Result.CompletionTimeSeconds = 300.f;
	TestTrue(TEXT("Mission completion generates persistent state"), Source->CompleteActiveMission(Result));
	TestTrue(TEXT("Campaign writes to a unique disk slot"), Source->SaveCampaignToSlot(SlotName, UserIndex));
	TestTrue(TEXT("Save system reports the unique slot"), UGameplayStatics::DoesSaveGameExist(SlotName, UserIndex));

	UGameInstance* TargetGameInstance = NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Target =
		NewObject<USkyguardCampaignSubsystem>(TargetGameInstance);
	TestTrue(TEXT("Target campaign configures"), Target->ConfigureCampaign(Campaign));
	TestTrue(TEXT("Target reloads disk slot"), Target->LoadCampaignFromSlot(SlotName, UserIndex));
	TestTrue(TEXT("Disk round trip restores Mission 2 unlock"), Target->CanStartMission(TEXT("M02")));
	TestEqual(TEXT("Disk round trip restores earned medals"), Target->GetEarnedCampaignMedals(), Result.MedalTier);

	TestFalse(TEXT("Empty slot names are rejected"), Target->SaveCampaignToSlot(TEXT("  "), UserIndex));
	TestFalse(TEXT("Traversal slot names are rejected"), Target->SaveCampaignToSlot(TEXT("../unsafe"), UserIndex));
	TestFalse(TEXT("Negative user index is rejected"), Target->LoadCampaignFromSlot(SlotName, -1));
	TestTrue(TEXT("Automation slot is deleted after verification"), Target->DeleteCampaignSlot(SlotName, UserIndex));
	TestFalse(TEXT("Deleted automation slot no longer exists"), UGameplayStatics::DoesSaveGameExist(SlotName, UserIndex));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignFailAndCombatStatsTest,
	"Skyguard52.Campaign.Sortie.FailDebriefAndCombatStatFill",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignFailAndCombatStatsTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCampaignTests;

	USkyguardCampaignDefinition* Campaign = MakeTwoMissionCampaign();
	UGameInstance* GameInstance =
		NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Runtime =
		NewObject<USkyguardCampaignSubsystem>(GameInstance);

	TestTrue(TEXT("Campaign configures"), Runtime->ConfigureCampaign(Campaign));
	TestTrue(TEXT("Mission 1 starts"), Runtime->StartMission(TEXT("M01")));

	ASkyguardGunner* Gunner =
		NewObject<ASkyguardGunner>(GetTransientPackage());
	Gunner->ResetSortieCombatStats();
	Gunner->RecordRifleShot();
	Gunner->RecordRifleShot();
	Gunner->RecordRifleHit();
	Gunner->RecordIglaShot();
	Gunner->RecordIglaHit();

	FSkyguardMissionResult CombatResult;
	Runtime->FillResultCombatStats(CombatResult, Gunner, nullptr);
	TestEqual(TEXT("Rifle and Igla shots are counted"), CombatResult.ShotsFired, 3);
	TestEqual(TEXT("Rifle and Igla hits are counted"), CombatResult.Hits, 2);
	TestEqual(
		TEXT("Aircraft damage stays zero without a Yak health API"),
		CombatResult.AircraftDamageFraction,
		0.f);

	TestTrue(
		TEXT("Protect objective can fail the sortie"),
		Runtime->FailObjective(TEXT("ProtectCity")));

	FSkyguardMissionResult FailResult;
	FailResult.ShotsFired = CombatResult.ShotsFired;
	FailResult.Hits = CombatResult.Hits;
	TestTrue(
		TEXT("Failed sortie builds a failure debrief"),
		Runtime->FailActiveMission(FailResult));

	const FSkyguardMissionDebrief& Debrief = Runtime->GetLastDebrief();
	TestEqual(
		TEXT("Failure debrief is presentation-ready"),
		Debrief.State,
		ESkyguardMissionDebriefState::Ready);
	TestFalse(TEXT("Failed sortie does not claim success"), Debrief.Result.bMissionSucceeded);
	TestEqual(TEXT("Failed sortie scores zero"), Debrief.Result.FinalScore, 0);
	TestFalse(TEXT("Failure does not persist unlock progress"), Debrief.bProgressSaved);
	TestTrue(
		TEXT("Failure narrative uses authored FailureDebrief"),
		Debrief.Narrative.EqualTo(
			FText::FromString(TEXT("Coastal defense failed."))));
	TestFalse(
		TEXT("Travel stays blocked after an unsaved failure"),
		Runtime->CanTravelToNextMission());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignLoadBeforeStartUnlockTest,
	"Skyguard52.Campaign.Persistence.LoadBeforeStartUnlocksNextMission",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignLoadBeforeStartUnlockTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCampaignTests;

	const FString SlotName = FString::Printf(
		TEXT("SkyguardLoadBeforeStart_%s"),
		*FGuid::NewGuid().ToString(EGuidFormats::Digits));

	USkyguardCampaignDefinition* Campaign = MakeTwoMissionCampaign();
	UGameInstance* SourceGameInstance =
		NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Source =
		NewObject<USkyguardCampaignSubsystem>(SourceGameInstance);
	TestTrue(TEXT("Source configures"), Source->ConfigureCampaign(Campaign));
	TestTrue(TEXT("Source starts M01"), Source->StartMission(TEXT("M01")));
	TestTrue(TEXT("Source completes objective 1"), Source->AddObjectiveProgress(TEXT("BossDefeated")));
	TestTrue(TEXT("Source completes objective 2"), Source->AddObjectiveProgress(TEXT("BossDefeated")));

	FSkyguardMissionResult Result;
	Result.ShotsFired = 5;
	Result.Hits = 5;
	Result.AircraftDamageFraction = 0.f;
	Result.CompletionTimeSeconds = 280.f;
	TestTrue(
		TEXT("Source finalizes and saves"),
		Source->FinalizeActiveMission(Result, SlotName, 0));
	TestTrue(
		TEXT("Source reports progress saved"),
		Source->GetLastDebrief().bProgressSaved);

	UGameInstance* FreshGameInstance =
		NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Fresh =
		NewObject<USkyguardCampaignSubsystem>(FreshGameInstance);
	TestTrue(TEXT("Fresh configures"), Fresh->ConfigureCampaign(Campaign));
	TestFalse(
		TEXT("Without load, M02 stays locked"),
		Fresh->CanStartMission(TEXT("M02")));
	TestTrue(
		TEXT("Fresh loads the saved slot before StartMission"),
		Fresh->LoadCampaignFromSlot(SlotName, 0));
	TestTrue(
		TEXT("After load, M02 unlocks for StartMission"),
		Fresh->CanStartMission(TEXT("M02")));
	TestTrue(
		TEXT("Fresh can start the unlocked next mission"),
		Fresh->StartMission(TEXT("M02")));
	TestTrue(TEXT("Cleanup slot"), Fresh->DeleteCampaignSlot(SlotName, 0));
	return true;
}

#endif
