#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMissionTypes.h"

#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRoutePointDefaultsTest,
	"Skyguard52.Mission.Types.RoutePointDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRoutePointDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardRoutePoint Point;
	TestEqual(TEXT("PointId defaults to NAME_None"), Point.PointId, NAME_None);
	TestTrue(
		TEXT("WorldLocation defaults to ZeroVector"),
		Point.WorldLocation.Equals(FVector::ZeroVector));
	TestEqual(TEXT("TargetAirspeedKph defaults to 220"), Point.TargetAirspeedKph, 220.f);
	TestEqual(TEXT("LookAheadSeconds defaults to 2"), Point.LookAheadSeconds, 2.f);
	TestTrue(TEXT("bAllowCombatOrbit defaults to true"), Point.bAllowCombatOrbit);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRouteDefinitionDefaultsTest,
	"Skyguard52.Mission.Types.RouteDefinitionDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRouteDefinitionDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardRouteDefinition Route;
	TestEqual(TEXT("RouteId defaults to NAME_None"), Route.RouteId, NAME_None);
	TestEqual(TEXT("Points defaults to empty"), Route.Points.Num(), 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardObjectiveDefinitionDefaultsTest,
	"Skyguard52.Mission.Types.ObjectiveDefinitionDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardObjectiveDefinitionDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardObjectiveDefinition Objective;
	TestEqual(TEXT("ObjectiveId defaults to NAME_None"), Objective.ObjectiveId, NAME_None);
	TestTrue(TEXT("DisplayName defaults to empty"), Objective.DisplayName.IsEmpty());
	TestEqual(
		TEXT("Type defaults to DestroyTargets"),
		Objective.Type,
		ESkyguardMissionObjectiveType::DestroyTargets);
	TestEqual(TEXT("RequiredProgress defaults to 1"), Objective.RequiredProgress, 1);
	TestTrue(
		TEXT("bRequiredForMissionSuccess defaults to true"),
		Objective.bRequiredForMissionSuccess);
	TestFalse(TEXT("bFailureEndsMission defaults to false"), Objective.bFailureEndsMission);
	TestEqual(TEXT("ScoreReward defaults to 1000"), Objective.ScoreReward, 1000);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardEnemyFormationDefinitionDefaultsTest,
	"Skyguard52.Mission.Types.EnemyFormationDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardEnemyFormationDefinitionDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardEnemyFormationDefinition Formation;
	TestEqual(TEXT("FormationId defaults to NAME_None"), Formation.FormationId, NAME_None);
	TestEqual(
		TEXT("Formation defaults to Vee"),
		Formation.Formation,
		ESkyguardFormationType::Vee);
	TestEqual(TEXT("UnitCount defaults to 3"), Formation.UnitCount, 3);
	TestEqual(
		TEXT("SpacingCentimeters defaults to 1200"),
		Formation.SpacingCentimeters,
		1200.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardEnemyWaveDefinitionDefaultsTest,
	"Skyguard52.Mission.Types.EnemyWaveDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardEnemyWaveDefinitionDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardEnemyWaveDefinition Wave;
	TestEqual(TEXT("WaveId defaults to NAME_None"), Wave.WaveId, NAME_None);
	TestEqual(TEXT("StartTimeSeconds defaults to 0"), Wave.StartTimeSeconds, 0.f);
	TestEqual(TEXT("Formations defaults to empty"), Wave.Formations.Num(), 0);
	TestEqual(
		TEXT("CompletionObjectiveId defaults to NAME_None"),
		Wave.CompletionObjectiveId,
		NAME_None);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardBossWeakPointDefinitionDefaultsTest,
	"Skyguard52.Mission.Types.BossWeakPointDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardBossWeakPointDefinitionDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardBossWeakPointDefinition WeakPoint;
	TestEqual(TEXT("WeakPointId defaults to NAME_None"), WeakPoint.WeakPointId, NAME_None);
	TestEqual(
		TEXT("ExposesWeakPointId defaults to NAME_None"),
		WeakPoint.ExposesWeakPointId,
		NAME_None);
	TestEqual(TEXT("Integrity defaults to 100"), WeakPoint.Integrity, 100.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardBossDefinitionDefaultsTest,
	"Skyguard52.Mission.Types.BossDefinitionDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardBossDefinitionDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardBossDefinition Boss;
	TestEqual(TEXT("BossId defaults to NAME_None"), Boss.BossId, NAME_None);
	TestTrue(TEXT("Callsign defaults to empty"), Boss.Callsign.IsEmpty());
	TestEqual(TEXT("WeakPoints defaults to empty"), Boss.WeakPoints.Num(), 0);
	TestEqual(
		TEXT("DefeatObjectiveId defaults to NAME_None"),
		Boss.DefeatObjectiveId,
		NAME_None);
	TestEqual(TEXT("MaximumBreakupPieces defaults to 3"), Boss.MaximumBreakupPieces, 3);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardWeatherProfileDefaultsTest,
	"Skyguard52.Mission.Types.WeatherProfileDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardWeatherProfileDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardWeatherProfile Weather;
	TestEqual(TEXT("ProfileId defaults to NAME_None"), Weather.ProfileId, NAME_None);
	TestEqual(
		TEXT("Weather defaults to Clear"),
		Weather.Weather,
		ESkyguardMissionWeather::Clear);
	TestEqual(TEXT("TimeOfDayHours defaults to 12"), Weather.TimeOfDayHours, 12.f);
	TestEqual(
		TEXT("WindSpeedMetersPerSecond defaults to 5"),
		Weather.WindSpeedMetersPerSecond,
		5.f);
	TestEqual(TEXT("Precipitation defaults to 0"), Weather.Precipitation, 0.f);
	TestEqual(TEXT("CloudCoverage defaults to 0.25"), Weather.CloudCoverage, 0.25f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionPresentationDefaultsTest,
	"Skyguard52.Mission.Types.MissionPresentationDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionPresentationDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardMissionPresentation Presentation;
	TestTrue(TEXT("Briefing defaults to empty"), Presentation.Briefing.IsEmpty());
	TestEqual(TEXT("RadioChatter defaults to empty"), Presentation.RadioChatter.Num(), 0);
	TestTrue(TEXT("SuccessDebrief defaults to empty"), Presentation.SuccessDebrief.IsEmpty());
	TestTrue(TEXT("FailureDebrief defaults to empty"), Presentation.FailureDebrief.IsEmpty());
	TestEqual(
		TEXT("MinimumBriefingWarmupSeconds defaults to 3"),
		Presentation.MinimumBriefingWarmupSeconds,
		3.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionScoreRulesDefaultsTest,
	"Skyguard52.Mission.Types.ScoreRulesDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionScoreRulesDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardMissionScoreRules ScoreRules;
	TestEqual(TEXT("CompletionScore defaults to 5000"), ScoreRules.CompletionScore, 5000);
	TestEqual(
		TEXT("PerfectAccuracyBonus defaults to 2500"),
		ScoreRules.PerfectAccuracyBonus,
		2500);
	TestEqual(TEXT("NoDamageBonus defaults to 1500"), ScoreRules.NoDamageBonus, 1500);
	TestEqual(TEXT("BronzeThreshold defaults to 5000"), ScoreRules.BronzeThreshold, 5000);
	TestEqual(TEXT("SilverThreshold defaults to 8000"), ScoreRules.SilverThreshold, 8000);
	TestEqual(TEXT("GoldThreshold defaults to 11000"), ScoreRules.GoldThreshold, 11000);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardObjectiveProgressDefaultsTest,
	"Skyguard52.Mission.Types.ObjectiveProgressDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardObjectiveProgressDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardObjectiveProgress Progress;
	TestEqual(TEXT("ObjectiveId defaults to NAME_None"), Progress.ObjectiveId, NAME_None);
	TestEqual(TEXT("CurrentProgress defaults to 0"), Progress.CurrentProgress, 0);
	TestEqual(
		TEXT("State defaults to Inactive"),
		Progress.State,
		ESkyguardMissionObjectiveState::Inactive);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionResultDefaultsTest,
	"Skyguard52.Mission.Types.MissionResultDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionResultDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardMissionResult Result;
	TestEqual(TEXT("MissionId defaults to NAME_None"), Result.MissionId, NAME_None);
	TestFalse(TEXT("bMissionSucceeded defaults to false"), Result.bMissionSucceeded);
	TestEqual(TEXT("ShotsFired defaults to 0"), Result.ShotsFired, 0);
	TestEqual(TEXT("Hits defaults to 0"), Result.Hits, 0);
	TestEqual(
		TEXT("AircraftDamageFraction defaults to 0"),
		Result.AircraftDamageFraction,
		0.f);
	TestEqual(
		TEXT("CompletionTimeSeconds defaults to 0"),
		Result.CompletionTimeSeconds,
		0.f);
	TestEqual(
		TEXT("CompletedObjectiveIds defaults to empty"),
		Result.CompletedObjectiveIds.Num(),
		0);
	TestEqual(TEXT("FinalScore defaults to 0"), Result.FinalScore, 0);
	TestEqual(TEXT("MedalTier defaults to 0"), Result.MedalTier, 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionDebriefDefaultsTest,
	"Skyguard52.Mission.Types.MissionDebriefDefaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionDebriefDefaultsTest::RunTest(const FString& Parameters)
{
	const FSkyguardMissionDebrief Debrief;
	TestEqual(
		TEXT("State defaults to Unavailable"),
		Debrief.State,
		ESkyguardMissionDebriefState::Unavailable);
	TestEqual(TEXT("Nested Result.MissionId is NAME_None"), Debrief.Result.MissionId, NAME_None);
	TestFalse(TEXT("Nested Result is not a success"), Debrief.Result.bMissionSucceeded);
	TestEqual(TEXT("Nested Result.FinalScore is 0"), Debrief.Result.FinalScore, 0);
	TestTrue(TEXT("MissionDisplayName defaults to empty"), Debrief.MissionDisplayName.IsEmpty());
	TestTrue(TEXT("Narrative defaults to empty"), Debrief.Narrative.IsEmpty());
	TestFalse(TEXT("bNewBestScore defaults to false"), Debrief.bNewBestScore);
	TestFalse(TEXT("bNewBestMedal defaults to false"), Debrief.bNewBestMedal);
	TestFalse(TEXT("bProgressSaved defaults to false"), Debrief.bProgressSaved);
	TestTrue(TEXT("SaveSlotName defaults to empty"), Debrief.SaveSlotName.IsEmpty());
	TestEqual(TEXT("NextMissionId defaults to NAME_None"), Debrief.NextMissionId, NAME_None);
	TestTrue(
		TEXT("NextMissionDisplayName defaults to empty"),
		Debrief.NextMissionDisplayName.IsEmpty());
	TestTrue(TEXT("NextMissionMap defaults to null"), Debrief.NextMissionMap.IsNull());
	TestFalse(TEXT("bNextMissionUnlocked defaults to false"), Debrief.bNextMissionUnlocked);
	TestFalse(TEXT("bCampaignComplete defaults to false"), Debrief.bCampaignComplete);
	return true;
}

#endif
