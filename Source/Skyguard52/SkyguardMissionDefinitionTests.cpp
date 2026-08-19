#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMissionDefinition.h"

#include "Misc/AutomationTest.h"

namespace SkyguardMissionDefinitionTests
{
	static const TCHAR* AuthoredMissionPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M01_CoastalIntercept.DA_Mission_M01_CoastalIntercept");

	bool HasError(const TArray<FText>& Errors, const TCHAR* ExactMessage)
	{
		return Errors.ContainsByPredicate(
			[ExactMessage](const FText& Error)
			{
				return Error.ToString() == ExactMessage;
			});
	}

	USkyguardMissionDefinition* MakeValidMission()
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>(GetTransientPackage());
		Mission->MissionId = TEXT("M01_DefinitionPublicApi");
		Mission->DisplayName = FText::FromString(TEXT("Definition Public API"));

		FSkyguardRoutePoint Start;
		Start.PointId = TEXT("Start");
		FSkyguardRoutePoint End;
		End.PointId = TEXT("End");
		End.WorldLocation = FVector(1000.f, 0.f, 0.f);
		Mission->Route.RouteId = TEXT("M01_DefinitionPublicApi_Route");
		Mission->Route.Points = { Start, End };

		FSkyguardObjectiveDefinition Required;
		Required.ObjectiveId = TEXT("ClearContact");
		Required.DisplayName = FText::FromString(TEXT("Clear contact"));
		Required.Type = ESkyguardMissionObjectiveType::DestroyTargets;
		Required.RequiredProgress = 1;
		Required.bRequiredForMissionSuccess = true;

		FSkyguardObjectiveDefinition Optional;
		Optional.ObjectiveId = TEXT("MarkEgress");
		Optional.DisplayName = FText::FromString(TEXT("Mark egress"));
		Optional.Type = ESkyguardMissionObjectiveType::ReachRoutePoint;
		Optional.RequiredProgress = 1;
		Optional.bRequiredForMissionSuccess = false;
		Mission->Objectives = { Required, Optional };
		return Mission;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionDefinitionInMemoryPublicApiTest,
	"Skyguard52.Campaign.MissionDefinition.InMemoryPublicApi",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionDefinitionInMemoryPublicApiTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMissionDefinitionTests;

	USkyguardMissionDefinition* EmptyMission =
		NewObject<USkyguardMissionDefinition>(GetTransientPackage());
	TestNotNull(TEXT("In-memory mission constructs"), EmptyMission);
	if (!EmptyMission)
	{
		return false;
	}

	TestEqual(
		TEXT("NewObject CampaignOrder defaults to 1"),
		EmptyMission->CampaignOrder,
		1);

	TArray<FText> EmptyErrors;
	TestFalse(
		TEXT("Empty mission fails ValidateDefinition"),
		EmptyMission->ValidateDefinition(EmptyErrors));
	TestTrue(
		TEXT("Empty mission emits at least one validation error"),
		EmptyErrors.Num() >= 1);
	TestTrue(
		TEXT("Empty mission reports MissionId must be set"),
		HasError(EmptyErrors, TEXT("MissionId must be set.")));
	TestTrue(
		TEXT("Empty mission reports DisplayName must be set"),
		HasError(EmptyErrors, TEXT("DisplayName must be set.")));
	TestTrue(
		TEXT("Empty mission reports route id and two points are required"),
		HasError(EmptyErrors, TEXT("Route requires an id and at least two points.")));
	TestTrue(
		TEXT("Empty mission reports a required objective is needed"),
		HasError(EmptyErrors, TEXT("At least one required objective is needed.")));

	TestNull(
		TEXT("FindObjective(NAME_None) on an empty mission is nullptr"),
		EmptyMission->FindObjective(NAME_None));
	TestNull(
		TEXT("FindObjective of an unknown id on an empty mission is nullptr"),
		EmptyMission->FindObjective(TEXT("UnknownObjective")));

	USkyguardMissionDefinition* Mission = MakeValidMission();
	TestNotNull(TEXT("Authored in-memory mission constructs"), Mission);
	if (!Mission)
	{
		return false;
	}

	TestEqual(
		TEXT("First route point TargetAirspeedKph defaults to 220"),
		Mission->Route.Points[0].TargetAirspeedKph,
		220.f);
	TestEqual(
		TEXT("Second route point TargetAirspeedKph defaults to 220"),
		Mission->Route.Points[1].TargetAirspeedKph,
		220.f);

	TestEqual(
		TEXT("FindObjective returns the matching first objective"),
		Mission->FindObjective(TEXT("ClearContact")),
		&Mission->Objectives[0]);
	TestEqual(
		TEXT("FindObjective returns the matching second objective"),
		Mission->FindObjective(TEXT("MarkEgress")),
		&Mission->Objectives[1]);
	TestNull(
		TEXT("FindObjective(NAME_None) on an authored mission is nullptr"),
		Mission->FindObjective(NAME_None));
	TestNull(
		TEXT("FindObjective of an unknown id on an authored mission is nullptr"),
		Mission->FindObjective(TEXT("UnknownObjective")));

	TArray<FText> AuthoredErrors;
	const bool bAuthoredValid = Mission->ValidateDefinition(AuthoredErrors);
	TestEqual(
		TEXT("ValidateDefinition return matches the empty-error contract"),
		bAuthoredValid,
		AuthoredErrors.IsEmpty());
	TestTrue(
		TEXT("MissionId, DisplayName, route, and a required objective pass ValidateDefinition"),
		bAuthoredValid);
	TestEqual(
		TEXT("Valid authored mission emits no errors"),
		AuthoredErrors.Num(),
		0);

	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionDefinitionAuthoredAssetTest,
	"Skyguard52.Campaign.MissionDefinition.AuthoredAssetIfPresent",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionDefinitionAuthoredAssetTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMissionDefinitionTests;

	USkyguardMissionDefinition* LoadedMission =
		LoadObject<USkyguardMissionDefinition>(
			nullptr,
			AuthoredMissionPath);
	if (!LoadedMission)
	{
		AddWarning(TEXT(
			"DA_Mission_M01_CoastalIntercept did not load; in-memory mission checks still apply."));
		return true;
	}

	TArray<FText> LoadedErrors;
	const bool bLoadedValid = LoadedMission->ValidateDefinition(LoadedErrors);
	TestEqual(
		TEXT("Loaded ValidateDefinition return matches the empty-error contract"),
		bLoadedValid,
		LoadedErrors.IsEmpty());

	TestNull(
		TEXT("FindObjective(NAME_None) on the loaded mission is nullptr"),
		LoadedMission->FindObjective(NAME_None));
	TestNull(
		TEXT("FindObjective of an unknown id on the loaded mission is nullptr"),
		LoadedMission->FindObjective(TEXT("UnknownObjective")));

	if (LoadedMission->Objectives.Num() > 0 &&
		!LoadedMission->Objectives[0].ObjectiveId.IsNone())
	{
		const FName FirstObjectiveId = LoadedMission->Objectives[0].ObjectiveId;
		TestEqual(
			TEXT("FindObjective of the first objective id returns that row"),
			LoadedMission->FindObjective(FirstObjectiveId),
			&LoadedMission->Objectives[0]);
	}

	return true;
}

#endif
