#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMissionTypes.h"
#include "SkyguardRouteRuntime.h"
#include "Misc/AutomationTest.h"

namespace SkyguardRouteRuntimeTests
{
	FSkyguardRouteDefinition MakeThreePointLRoute()
	{
		FSkyguardRouteDefinition Definition;
		Definition.RouteId = TEXT("AutomationSampleByDistance");

		FSkyguardRoutePoint Start;
		Start.PointId = TEXT("Start");
		Start.WorldLocation = FVector(0.f, 0.f, 80.f);

		FSkyguardRoutePoint Corner;
		Corner.PointId = TEXT("Corner");
		Corner.WorldLocation = FVector(1500.f, 0.f, 80.f);

		FSkyguardRoutePoint End;
		End.PointId = TEXT("End");
		End.WorldLocation = FVector(1500.f, 1500.f, 80.f);

		Definition.Points = { Start, Corner, End };
		return Definition;
	}

	float PolylineLength(const TArray<FSkyguardRoutePoint>& Points)
	{
		float Length = 0.f;
		for (int32 Index = 1; Index < Points.Num(); ++Index)
		{
			Length += FVector::Distance(
				Points[Index - 1].WorldLocation,
				Points[Index].WorldLocation);
		}
		return Length;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRouteRuntimeSampleByDistanceTest,
	"Skyguard52.Route.Runtime.SampleLocationByDistanceHitsStartMidpointAndEnd",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRouteRuntimeSampleByDistanceTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRouteRuntimeTests;

	const FSkyguardRouteDefinition Definition = MakeThreePointLRoute();
	const float ExpectedLength = PolylineLength(Definition.Points);
	const FVector StartLocation = Definition.Points[0].WorldLocation;
	const FVector CornerLocation = Definition.Points[1].WorldLocation;
	const FVector EndLocation = Definition.Points[2].WorldLocation;
	const float HalfLength = ExpectedLength * 0.5f;

	USkyguardRouteRuntime* Route = NewObject<USkyguardRouteRuntime>(GetTransientPackage());
	TestNotNull(TEXT("Route runtime object is created"), Route);
	if (!Route)
	{
		return false;
	}

	TestTrue(TEXT("Three-point route initializes"), Route->InitializeRoute(Definition));
	TestEqual(
		TEXT("GetRouteLength matches the polyline"),
		Route->GetRouteLength(),
		ExpectedLength);
	TestTrue(
		TEXT("SampleLocationByDistance at 0 hits the start"),
		Route->SampleLocationByDistance(0.f).Equals(StartLocation, 0.01f));
	TestTrue(
		TEXT("SampleLocationByDistance at half length hits the polyline midpoint"),
		Route->SampleLocationByDistance(HalfLength).Equals(CornerLocation, 0.01f));
	TestTrue(
		TEXT("SampleLocationByDistance at route length hits the end"),
		Route->SampleLocationByDistance(ExpectedLength).Equals(EndLocation, 0.01f));

	return true;
}

#endif
