#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignSaveGame.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardCampaignPersistenceContractTests.cpp.
// Remaining empty-save NewObject public defaults and already-current
// identity migrate only. Existing
// SkyguardCampaignPersistenceContractTests.cpp already covers
// v1→v2 upgrade, reject version 0, and reject version 99.
// NewObject only. No world, no disk (no SaveGameToSlot /
// LoadGameFromSlot), no Gunner / Yak / Igla / rifle.
// Does not invent INDEX_NONE.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignSaveGameEmptyFailClosedTest,
	"Skyguard52.Campaign.Persistence.EmptySaveGameFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignSaveGameEmptyFailClosedTest::RunTest(const FString& Parameters)
{
	TestEqual(
		TEXT("MinSupportedSaveVersion is the v1 layout"),
		USkyguardCampaignSaveGame::MinSupportedSaveVersion,
		1);
	TestEqual(
		TEXT("CurrentSaveVersion stays on the v2 contract"),
		USkyguardCampaignSaveGame::CurrentSaveVersion,
		2);

	USkyguardCampaignSaveGame* Save = NewObject<USkyguardCampaignSaveGame>();
	TestNotNull(TEXT("NewObject campaign save constructs"), Save);
	if (!Save)
	{
		return false;
	}

	TestEqual(
		TEXT("NewObject SaveVersion is CurrentSaveVersion"),
		Save->SaveVersion,
		USkyguardCampaignSaveGame::CurrentSaveVersion);
	TestEqual(TEXT("NewObject SaveVersion is 2"), Save->SaveVersion, 2);
	TestEqual(TEXT("NewObject CampaignId is NAME_None"), Save->CampaignId, NAME_None);
	TestEqual(TEXT("NewObject MissionRecords is empty"), Save->MissionRecords.Num(), 0);

	const FSkyguardMissionSaveRecord DefaultRecord;
	TestFalse(TEXT("Default mission record bCompleted is false"), DefaultRecord.bCompleted);
	TestEqual(TEXT("Default mission record BestScore is 0"), DefaultRecord.BestScore, 0);
	TestEqual(TEXT("Default mission record BestMedalTier is 0"), DefaultRecord.BestMedalTier, 0);
	TestEqual(
		TEXT("Default mission record BestCompletionTimeSeconds is 0"),
		DefaultRecord.BestCompletionTimeSeconds,
		0.f);

	TestTrue(
		TEXT("MigrateCampaignSave returns true on an already-v2 empty save"),
		USkyguardCampaignSaveGame::MigrateCampaignSave(*Save));
	TestEqual(
		TEXT("Identity migrate leaves SaveVersion 2 (v1 walk is skipped)"),
		Save->SaveVersion,
		2);
	TestEqual(
		TEXT("Identity migrate leaves SaveVersion on CurrentSaveVersion"),
		Save->SaveVersion,
		USkyguardCampaignSaveGame::CurrentSaveVersion);
	TestEqual(
		TEXT("Identity migrate leaves CampaignId NAME_None"),
		Save->CampaignId,
		NAME_None);
	TestEqual(
		TEXT("Identity migrate leaves MissionRecords empty"),
		Save->MissionRecords.Num(),
		0);

	return true;
}

#endif
