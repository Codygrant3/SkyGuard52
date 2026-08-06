#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardMissionDefinition.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMissionMapAssemblyTests
{
	class FScopedWorld
	{
	public:
		FScopedWorld()
		{
			World = UWorld::CreateWorld(EWorldType::Game, false, TEXT("SkyguardMissionMapAssemblyTestWorld"));
			check(World);
			FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}
		~FScopedWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
		}
		UWorld* Get() const { return World; }
	private:
		UWorld* World = nullptr;
	};

	USkyguardMissionDefinition* MakeDefinition()
	{
		USkyguardMissionDefinition* Mission = NewObject<USkyguardMissionDefinition>();
		Mission->MissionId = TEXT("M02_HarborShield");
		Mission->DisplayName = FText::FromString(TEXT("Harbor Shield"));
		Mission->CampaignOrder = 2;
		Mission->Route.RouteId = TEXT("M02_Route");
		for (int32 Index = 0; Index < 4; ++Index)
		{
			FSkyguardRoutePoint Point;
			Point.PointId = FName(*FString::Printf(TEXT("P%d"), Index));
			Point.WorldLocation = FVector(Index * 12000.f, Index * 1000.f, 5000.f);
			Mission->Route.Points.Add(Point);
		}
		FSkyguardObjectiveDefinition Protect;
		Protect.ObjectiveId = TEXT("ProtectFuelTerminal");
		Protect.DisplayName = FText::FromString(TEXT("Protect Fuel Terminal"));
		Protect.bRequiredForMissionSuccess = true;
		Protect.bFailureEndsMission = true;
		FSkyguardObjectiveDefinition Boss;
		Boss.ObjectiveId = TEXT("DefeatBreakwater");
		Boss.DisplayName = FText::FromString(TEXT("Defeat Breakwater"));
		Boss.Type = ESkyguardMissionObjectiveType::BossPhase;
		Boss.bRequiredForMissionSuccess = true;
		Mission->Objectives = { Protect, Boss };
		Mission->Boss.BossId = TEXT("Breakwater");
		Mission->Boss.DefeatObjectiveId = TEXT("DefeatBreakwater");
		Mission->Weather.ProfileId = TEXT("TestHarborWeather");
		FSkyguardBossWeakPointDefinition Engine;
		Engine.WeakPointId = TEXT("Engine");
		Engine.RequiredWeapon = TEXT("Igla");
		Mission->Boss.WeakPoints = { Engine };
		return Mission;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMissionMapAssemblyValidationTest,
	"Skyguard52.CampaignMaps.Assembly.ValidatedDefinitionAndDistinctLandmarks",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMissionMapAssemblyValidationTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardMissionMapAssemblyTests;
	FScopedWorld World;
	ASkyguardMissionMapAssemblyDirector* Director =
		World.Get()->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	USkyguardMissionDefinition* Definition = MakeDefinition();
	Director->MissionDefinition = Definition;
	Director->MissionId = Definition->MissionId;
	Director->WeatherProfileId = Definition->Weather.ProfileId;
	for (const FSkyguardRoutePoint& Point : Definition->Route.Points)
	{
		Director->RoutePoints.Add(Point.WorldLocation);
	}
	FSkyguardMissionObjectiveAnchor Protect;
	Protect.ObjectiveId = TEXT("ProtectFuelTerminal");
	Protect.WorldLocation = FVector(30000.f, 12000.f, 0.f);
	FSkyguardMissionObjectiveAnchor Boss;
	Boss.ObjectiveId = TEXT("DefeatBreakwater");
	Boss.WorldLocation = FVector(24000.f, -6000.f, 4500.f);
	Director->ObjectiveAnchors = { Protect, Boss };
	for (int32 Index = 0; Index < 3; ++Index)
	{
		FSkyguardMissionLandmarkAnchor Landmark;
		Landmark.LandmarkId = FName(*FString::Printf(TEXT("Landmark%d"), Index));
		Landmark.Role = FName(*FString::Printf(TEXT("Role%d"), Index));
		Landmark.bMissionExclusive = Index < 2;
		Director->LandmarkAnchors.Add(Landmark);
	}

	TArray<FText> Errors;
	TestTrue(TEXT("Complete assembly validates"), Director->ValidateAssembly(Errors));
	TestEqual(TEXT("Four route points bind"), Director->GetReadiness().RoutePointCount, 4);
	TestTrue(TEXT("Required objectives are anchored"), Director->GetReadiness().bRequiredObjectivesAnchored);
	TestTrue(TEXT("Landmark roles are distinct"), Director->GetReadiness().bLandmarksDistinct);
	TestTrue(TEXT("Point near segment is inside flight clearance"),
		Director->IsPointInsideFlightClearance(FVector(6000.f, 500.f, 5000.f)));
	TestFalse(TEXT("Distant landmark is outside flight clearance"),
		Director->IsPointInsideFlightClearance(FVector(6000.f, 18000.f, 0.f)));

	Director->RoutePoints[1].Y += 5000.f;
	TestFalse(TEXT("Route drift from DataAsset is rejected"), Director->ValidateAssembly(Errors));
	return true;
}

#endif
