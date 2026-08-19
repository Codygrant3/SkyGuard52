#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSaveGame.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardMissionDefinition.h"
#include "Engine/GameInstance.h"
#include "Misc/AutomationTest.h"

namespace SkyguardCampaignPersistenceContractTests
{
	USkyguardCampaignDefinition* MakeMinimalCampaign()
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>(GetTransientPackage());
		Mission->MissionId = TEXT("M01");
		Mission->DisplayName = FText::FromString(TEXT("Persistence Contract"));
		Mission->CampaignOrder = 1;

		FSkyguardRoutePoint Start;
		Start.PointId = TEXT("Start");
		FSkyguardRoutePoint End;
		End.PointId = TEXT("End");
		End.WorldLocation = FVector(1000.f, 0.f, 0.f);
		Mission->Route.RouteId = TEXT("M01_Route");
		Mission->Route.Points = { Start, End };

		FSkyguardObjectiveDefinition Objective;
		Objective.ObjectiveId = TEXT("Hold");
		Objective.DisplayName = FText::FromString(TEXT("Hold"));
		Mission->Objectives = { Objective };

		USkyguardCampaignDefinition* Campaign =
			NewObject<USkyguardCampaignDefinition>(GetTransientPackage());
		Campaign->CampaignId = TEXT("PersistenceContractCampaign");
		Campaign->DisplayName = FText::FromString(TEXT("Persistence Contract"));
		Campaign->Missions = { Mission };
		return Campaign;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignSaveMigrationContractTest,
	"Skyguard52.Campaign.Persistence.MigrateCampaignSaveVersions",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignSaveMigrationContractTest::RunTest(const FString& Parameters)
{
	TestEqual(
		TEXT("CurrentSaveVersion stays on the v2 contract"),
		USkyguardCampaignSaveGame::CurrentSaveVersion,
		2);
	TestEqual(
		TEXT("MinSupportedSaveVersion is the v1 layout"),
		USkyguardCampaignSaveGame::MinSupportedSaveVersion,
		1);

	USkyguardCampaignSaveGame* Legacy =
		NewObject<USkyguardCampaignSaveGame>(GetTransientPackage());
	Legacy->SaveVersion = 1;
	TestTrue(
		TEXT("MigrateCampaignSave upgrades SaveVersion 1"),
		USkyguardCampaignSaveGame::MigrateCampaignSave(*Legacy));
	TestEqual(
		TEXT("SaveVersion 1 becomes CurrentSaveVersion (2)"),
		Legacy->SaveVersion,
		USkyguardCampaignSaveGame::CurrentSaveVersion);

	USkyguardCampaignSaveGame* PreMin =
		NewObject<USkyguardCampaignSaveGame>(GetTransientPackage());
	PreMin->SaveVersion = 0;
	TestFalse(
		TEXT("MigrateCampaignSave rejects SaveVersion 0"),
		USkyguardCampaignSaveGame::MigrateCampaignSave(*PreMin));
	TestEqual(TEXT("Rejected SaveVersion 0 is left unchanged"), PreMin->SaveVersion, 0);

	USkyguardCampaignSaveGame* Future =
		NewObject<USkyguardCampaignSaveGame>(GetTransientPackage());
	Future->SaveVersion = 99;
	TestFalse(
		TEXT("MigrateCampaignSave rejects future SaveVersion 99"),
		USkyguardCampaignSaveGame::MigrateCampaignSave(*Future));
	TestEqual(TEXT("Rejected SaveVersion 99 is left unchanged"), Future->SaveVersion, 99);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignSlotNameSanitizationContractTest,
	"Skyguard52.Campaign.Persistence.IsValidCampaignSlotName",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignSlotNameSanitizationContractTest::RunTest(
	const FString& Parameters)
{
	TestTrue(
		TEXT("Default Skyguard52Campaign slot is accepted"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(
			TEXT("Skyguard52Campaign")));

	TestFalse(
		TEXT("Empty slot names are rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("")));
	TestFalse(
		TEXT("Whitespace-only slot names are rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("  ")));
	TestFalse(
		TEXT("Leading or trailing spaces are rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(
			TEXT(" Skyguard52Campaign")));

	TestFalse(
		TEXT("Forward-slash path separators are rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("slot/name")));
	TestFalse(
		TEXT("Backslash path separators are rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("slot\\name")));
	TestFalse(
		TEXT("Parent-traversal slot names are rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("../unsafe")));

	// IsValidCampaignSlotName requires FPaths::MakeValidFileName to be a no-op.
	// These reserved / illegal filename characters are rewritten, so they fail.
	TestFalse(
		TEXT("Colon reserved filename character is rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("CON:")));
	TestFalse(
		TEXT("Asterisk reserved filename character is rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("slot*name")));
	TestFalse(
		TEXT("Question-mark reserved filename character is rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("slot?name")));
	TestFalse(
		TEXT("Pipe reserved filename character is rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("slot|name")));
	TestFalse(
		TEXT("Angle-bracket reserved filename characters are rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("<slot>")));
	TestFalse(
		TEXT("Quote reserved filename character is rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TEXT("slot\"name")));

	FString TooLong;
	TooLong.Reserve(65);
	for (int32 Index = 0; Index < 65; ++Index)
	{
		TooLong.AppendChar(TEXT('A'));
	}
	TestFalse(
		TEXT("Slot names longer than 64 characters are rejected"),
		USkyguardCampaignSubsystem::IsValidCampaignSlotName(TooLong));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignApplySaveGameVersionContractTest,
	"Skyguard52.Campaign.Persistence.ApplySaveGameVersionGate",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignApplySaveGameVersionContractTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardCampaignPersistenceContractTests;

	USkyguardCampaignDefinition* Campaign = MakeMinimalCampaign();
	UGameInstance* GameInstance = NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Runtime =
		NewObject<USkyguardCampaignSubsystem>(GameInstance);
	TestTrue(
		TEXT("Minimal campaign configures a NewObject subsystem"),
		Runtime->ConfigureCampaign(Campaign));

	USkyguardCampaignSaveGame* Current =
		NewObject<USkyguardCampaignSaveGame>(GetTransientPackage());
	Current->SaveVersion = USkyguardCampaignSaveGame::CurrentSaveVersion;
	Current->CampaignId = Campaign->CampaignId;
	TestTrue(
		TEXT("Current-version save applies on a NewObject subsystem"),
		Runtime->ApplySaveGame(Current));

	USkyguardCampaignSaveGame* Future =
		NewObject<USkyguardCampaignSaveGame>(GetTransientPackage());
	Future->SaveVersion = 99;
	Future->CampaignId = Campaign->CampaignId;
	TestFalse(
		TEXT("Future-version save is refused by ApplySaveGame"),
		Runtime->ApplySaveGame(Future));
	TestEqual(
		TEXT("Refused future save keeps SaveVersion 99"),
		Future->SaveVersion,
		99);
	return true;
}

#endif
