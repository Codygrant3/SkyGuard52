#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMissionTypes.h"
#include "SkyguardRouteRuntime.h"
#include "Misc/AutomationTest.h"

namespace SkyguardRouteRuntimePolylineTests
{
	FSkyguardRouteDefinition MakeThreePointPolyline()
	{
		FSkyguardRouteDefinition Definition;
		Definition.RouteId = TEXT("RouteRuntimePolyline");

		FSkyguardRoutePoint Start;
		Start.PointId = TEXT("Start");
		Start.WorldLocation = FVector(0.f, 0.f, 120.f);

		FSkyguardRoutePoint Knee;
		Knee.PointId = TEXT("Knee");
		Knee.WorldLocation = FVector(800.f, 0.f, 120.f);

		FSkyguardRoutePoint End;
		End.PointId = TEXT("End");
		End.WorldLocation = FVector(800.f, 600.f, 120.f);

		Definition.Points = { Start, Knee, End };
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
	FSkyguardRouteRuntimePolylineSampleTest,
	"Skyguard52.Route.Runtime.GetRouteLengthAndSampleHitsStartMidpointAndEnd",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRouteRuntimePolylineSampleTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRouteRuntimePolylineTests;

	const FSkyguardRouteDefinition Definition = MakeThreePointPolyline();
	const float ExpectedLength = PolylineLength(Definition.Points);
	const FVector StartLocation = Definition.Points[0].WorldLocation;
	const FVector MidpointLocation = FVector(700.f, 0.f, 120.f);
	const FVector EndLocation = Definition.Points.Last().WorldLocation;

	USkyguardRouteRuntime* Route = NewObject<USkyguardRouteRuntime>(GetTransientPackage());
	TestNotNull(TEXT("Route runtime object is created"), Route);
	if (!Route)
	{
		return false;
	}

	TestTrue(TEXT("Three-point route initializes"), Route->InitializeRoute(Definition));
	TestEqual(
		TEXT("Independent polyline sum is 1400 cm"),
		ExpectedLength,
		1400.f);
	TestEqual(
		TEXT("GetRouteLength matches the polyline"),
		Route->GetRouteLength(),
		ExpectedLength);
	TestTrue(
		TEXT("SampleLocationByDistance at 0 hits the start"),
		Route->SampleLocationByDistance(0.f).Equals(StartLocation, 0.01f));
	TestTrue(
		TEXT("SampleLocationByDistance at half length hits the midpoint"),
		Route->SampleLocationByDistance(ExpectedLength * 0.5f).Equals(MidpointLocation, 0.01f));
	TestTrue(
		TEXT("SampleLocationByDistance at route length hits the end"),
		Route->SampleLocationByDistance(ExpectedLength).Equals(EndLocation, 0.01f));

	return true;
}

#endif
