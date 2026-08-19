#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignDefinition.h"
#include "SkyguardMissionDefinition.h"

#include "Misc/AutomationTest.h"

namespace SkyguardCampaignDefinitionTests
{
	static const TCHAR* AuthoredCampaignPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Campaign_Skyguard52.DA_Campaign_Skyguard52");

	static const FName AuthoredM01Id = TEXT("M01_CoastalIntercept");

	USkyguardMissionDefinition* MakeValidMission(
		const FName MissionId,
		const int32 CampaignOrder)
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>(GetTransientPackage());
		Mission->MissionId = MissionId;
		Mission->DisplayName = FText::FromName(MissionId);
		Mission->CampaignOrder = CampaignOrder;

		FSkyguardRoutePoint Start;
		Start.PointId = TEXT("Start");
		FSkyguardRoutePoint End;
		End.PointId = TEXT("End");
		End.WorldLocation = FVector(1000.f, 0.f, 0.f);
		Mission->Route.RouteId = FName(*FString::Printf(
			TEXT("%s_Route"),
			*MissionId.ToString()));
		Mission->Route.Points = { Start, End };

		FSkyguardObjectiveDefinition Objective;
		Objective.ObjectiveId = TEXT("ClearContact");
		Objective.DisplayName = FText::FromString(TEXT("Clear contact"));
		Objective.Type = ESkyguardMissionObjectiveType::DestroyTargets;
		Objective.RequiredProgress = 1;
		Objective.bRequiredForMissionSuccess = true;
		Mission->Objectives = { Objective };
		return Mission;
	}

	USkyguardMissionDefinition* FindMissionInList(
		const USkyguardCampaignDefinition* Campaign,
		const FName MissionId)
	{
		if (!Campaign)
		{
			return nullptr;
		}
		for (const TObjectPtr<USkyguardMissionDefinition>& Mission : Campaign->Missions)
		{
			if (Mission && Mission->MissionId == MissionId)
			{
				return Mission.Get();
			}
		}
		return nullptr;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignDefinitionInMemoryPublicApiTest,
	"Skyguard52.Campaign.Definition.InMemoryPublicApi",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignDefinitionInMemoryPublicApiTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardCampaignDefinitionTests;

	USkyguardCampaignDefinition* EmptyCampaign =
		NewObject<USkyguardCampaignDefinition>(GetTransientPackage());
	TestNotNull(TEXT("In-memory campaign constructs"), EmptyCampaign);
	if (!EmptyCampaign)
	{
		return false;
	}

	TestEqual(
		TEXT("NewObject campaign default CampaignId is Skyguard52MainCampaign"),
		EmptyCampaign->CampaignId,
		FName(TEXT("Skyguard52MainCampaign")));

	TArray<FText> EmptyErrors;
	TestFalse(
		TEXT("Empty campaign fails ValidateDefinition"),
		EmptyCampaign->ValidateDefinition(EmptyErrors));
	TestTrue(
		TEXT("Empty campaign emits at least one validation error"),
		EmptyErrors.Num() >= 1);
	TestTrue(
		TEXT("Empty campaign reports that a mission is required"),
		EmptyErrors.ContainsByPredicate(
			[](const FText& Error)
			{
				return Error.ToString() == TEXT("Campaign requires at least one mission.");
			}));

	TestNull(
		TEXT("FindMission(NAME_None) on an empty campaign is nullptr"),
		EmptyCampaign->FindMission(NAME_None));
	TestNull(
		TEXT("FindMission of an unknown id on an empty campaign is nullptr"),
		EmptyCampaign->FindMission(TEXT("UnknownMission")));

	USkyguardMissionDefinition* MissionA =
		MakeValidMission(TEXT("M01_DefinitionAlpha"), 1);
	USkyguardMissionDefinition* MissionB =
		MakeValidMission(TEXT("M02_DefinitionBravo"), 2);
	TestNotNull(TEXT("First in-memory mission constructs"), MissionA);
	TestNotNull(TEXT("Second in-memory mission constructs"), MissionB);
	if (!MissionA || !MissionB)
	{
		return false;
	}

	TArray<FText> MissionAErrors;
	TArray<FText> MissionBErrors;
	TestTrue(
		TEXT("First mission is valid enough for the campaign validator"),
		MissionA->ValidateDefinition(MissionAErrors));
	TestTrue(
		TEXT("Second mission is valid enough for the campaign validator"),
		MissionB->ValidateDefinition(MissionBErrors));

	USkyguardCampaignDefinition* TwoMissionCampaign =
		NewObject<USkyguardCampaignDefinition>(GetTransientPackage());
	TestNotNull(TEXT("Two-mission campaign constructs"), TwoMissionCampaign);
	if (!TwoMissionCampaign)
	{
		return false;
	}
	TwoMissionCampaign->DisplayName = FText::FromString(TEXT("Definition Public API"));
	TwoMissionCampaign->Missions = { MissionA, MissionB };

	TestEqual(
		TEXT("FindMission returns the matching first mission"),
		TwoMissionCampaign->FindMission(TEXT("M01_DefinitionAlpha")),
		MissionA);
	TestEqual(
		TEXT("FindMission returns the matching second mission"),
		TwoMissionCampaign->FindMission(TEXT("M02_DefinitionBravo")),
		MissionB);
	TestNull(
		TEXT("FindMission(NAME_None) on a two-mission campaign is nullptr"),
		TwoMissionCampaign->FindMission(NAME_None));
	TestNull(
		TEXT("FindMission of an unknown id on a two-mission campaign is nullptr"),
		TwoMissionCampaign->FindMission(TEXT("UnknownMission")));

	TArray<FText> TwoMissionErrors;
	const bool bTwoMissionValid =
		TwoMissionCampaign->ValidateDefinition(TwoMissionErrors);
	TestEqual(
		TEXT("ValidateDefinition return matches the empty-error contract"),
		bTwoMissionValid,
		TwoMissionErrors.IsEmpty());
	TestTrue(
		TEXT("Two valid, uniquely ordered missions pass ValidateDefinition"),
		bTwoMissionValid);
	TestEqual(
		TEXT("Valid two-mission campaign emits no errors"),
		TwoMissionErrors.Num(),
		0);

	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignDefinitionAuthoredAssetTest,
	"Skyguard52.Campaign.Definition.AuthoredAssetIfPresent",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignDefinitionAuthoredAssetTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardCampaignDefinitionTests;

	USkyguardCampaignDefinition* LoadedCampaign =
		LoadObject<USkyguardCampaignDefinition>(
			nullptr,
			AuthoredCampaignPath);
	if (!LoadedCampaign)
	{
		AddWarning(TEXT(
			"DA_Campaign_Skyguard52 did not load; in-memory campaign checks still apply."));
		return true;
	}

	TArray<FText> LoadedErrors;
	const bool bLoadedValid = LoadedCampaign->ValidateDefinition(LoadedErrors);
	TestEqual(
		TEXT("Loaded ValidateDefinition return matches the empty-error contract"),
		bLoadedValid,
		LoadedErrors.IsEmpty());

	USkyguardMissionDefinition* FoundM01 =
		LoadedCampaign->FindMission(AuthoredM01Id);
	TestEqual(
		TEXT("FindMission(M01_CoastalIntercept) follows the authored mission list"),
		FoundM01,
		FindMissionInList(LoadedCampaign, AuthoredM01Id));

	if (LoadedCampaign->Missions.Num() > 0 && LoadedCampaign->Missions[0])
	{
		const FName FirstMissionId = LoadedCampaign->Missions[0]->MissionId;
		TestEqual(
			TEXT("FindMission of the first mission id returns that mission"),
			LoadedCampaign->FindMission(FirstMissionId),
			LoadedCampaign->Missions[0].Get());
	}

	return true;
}

#endif
