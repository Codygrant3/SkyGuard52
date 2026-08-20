#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMissionTypes.h"
#include "SkyguardRouteRuntime.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardRouteRuntimeTests.cpp.
// Fail-closed public API only: NewObject defaults, 0/1/coincident
// InitializeRoute, and clamp sampling. No world, no Gunner/Yak/Igla.

namespace SkyguardRouteRuntimeFailClosedTests
{
	FSkyguardRoutePoint MakePoint(const FName PointId, const FVector WorldLocation)
	{
		FSkyguardRoutePoint Point;
		Point.PointId = PointId;
		Point.WorldLocation = WorldLocation;
		return Point;
	}

	FSkyguardRouteDefinition MakeDefinition(
		const FName RouteId,
		const TArray<FSkyguardRoutePoint>& Points)
	{
		FSkyguardRouteDefinition Definition;
		Definition.RouteId = RouteId;
		Definition.Points = Points;
		return Definition;
	}

	USkyguardRouteRuntime* MakeRuntime()
	{
		return NewObject<USkyguardRouteRuntime>(GetTransientPackage());
	}

	bool ExpectZeroLengthAndZeroSamples(
		FAutomationTestBase& Test,
		const USkyguardRouteRuntime& Route)
	{
		const bool bLength = Test.TestEqual(
			TEXT("GetRouteLength is 0"),
			Route.GetRouteLength(),
			0.f);
		const bool bZero = Test.TestTrue(
			TEXT("SampleLocationByDistance(0) is ZeroVector"),
			Route.SampleLocationByDistance(0.f).Equals(FVector::ZeroVector, 0.01f));
		const bool bNegative = Test.TestTrue(
			TEXT("SampleLocationByDistance(-100) is ZeroVector"),
			Route.SampleLocationByDistance(-100.f).Equals(FVector::ZeroVector, 0.01f));
		const bool bHuge = Test.TestTrue(
			TEXT("SampleLocationByDistance(1e9) is ZeroVector"),
			Route.SampleLocationByDistance(1.0e9f).Equals(FVector::ZeroVector, 0.01f));
		return bLength && bZero && bNegative && bHuge;
	}

	bool ExpectConstantSample(
		FAutomationTestBase& Test,
		const USkyguardRouteRuntime& Route,
		const FVector ExpectedLocation)
	{
		const bool bZero = Test.TestTrue(
			TEXT("SampleLocationByDistance(0) returns the lone point"),
			Route.SampleLocationByDistance(0.f).Equals(ExpectedLocation, 0.01f));
		const bool bNegative = Test.TestTrue(
			TEXT("SampleLocationByDistance(-100) returns the lone point"),
			Route.SampleLocationByDistance(-100.f).Equals(ExpectedLocation, 0.01f));
		const bool bHuge = Test.TestTrue(
			TEXT("SampleLocationByDistance(1e9) returns the lone point"),
			Route.SampleLocationByDistance(1.0e9f).Equals(ExpectedLocation, 0.01f));
		return bZero && bNegative && bHuge;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRouteRuntimeNewObjectDefaultsTest,
	"Skyguard52.Route.Runtime.NewObjectDefaultsAreEmpty",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRouteRuntimeNewObjectDefaultsTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRouteRuntimeFailClosedTests;

	USkyguardRouteRuntime* Route = MakeRuntime();
	TestNotNull(TEXT("NewObject route runtime is created"), Route);
	if (!Route)
	{
		return false;
	}

	return ExpectZeroLengthAndZeroSamples(*this, *Route);
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRouteRuntimeInitializeZeroPointsTest,
	"Skyguard52.Route.Runtime.InitializeZeroPointsFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRouteRuntimeInitializeZeroPointsTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRouteRuntimeFailClosedTests;

	USkyguardRouteRuntime* Route = MakeRuntime();
	TestNotNull(TEXT("zero-point route runtime is created"), Route);
	if (!Route)
	{
		return false;
	}

	const FSkyguardRouteDefinition Definition = MakeDefinition(TEXT("EmptyRoute"), {});
	TestFalse(TEXT("InitializeRoute with 0 points returns false"), Route->InitializeRoute(Definition));
	return ExpectZeroLengthAndZeroSamples(*this, *Route);
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRouteRuntimeInitializeOnePointTest,
	"Skyguard52.Route.Runtime.InitializeOnePointFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRouteRuntimeInitializeOnePointTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRouteRuntimeFailClosedTests;

	USkyguardRouteRuntime* Route = MakeRuntime();
	TestNotNull(TEXT("one-point route runtime is created"), Route);
	if (!Route)
	{
		return false;
	}

	const FVector LoneLocation(250.f, -80.f, 40.f);
	const FSkyguardRouteDefinition Definition = MakeDefinition(
		TEXT("OnePointRoute"),
		{MakePoint(TEXT("Only"), LoneLocation)});
	TestFalse(TEXT("InitializeRoute with 1 point returns false"), Route->InitializeRoute(Definition));
	TestEqual(TEXT("one-point GetRouteLength stays 0"), Route->GetRouteLength(), 0.f);
	return ExpectConstantSample(*this, *Route, LoneLocation);
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRouteRuntimeInitializeCoincidentPointsTest,
	"Skyguard52.Route.Runtime.InitializeCoincidentPointsFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRouteRuntimeInitializeCoincidentPointsTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardRouteRuntimeFailClosedTests;

	USkyguardRouteRuntime* Route = MakeRuntime();
	TestNotNull(TEXT("coincident-point route runtime is created"), Route);
	if (!Route)
	{
		return false;
	}

	const FVector SharedLocation(400.f, 125.f, 90.f);
	const FSkyguardRouteDefinition Definition = MakeDefinition(
		TEXT("CoincidentRoute"),
		{
			MakePoint(TEXT("A"), SharedLocation),
			MakePoint(TEXT("B"), SharedLocation)
		});
	TestFalse(
		TEXT("InitializeRoute with 2 coincident points returns false"),
		Route->InitializeRoute(Definition));
	TestEqual(
		TEXT("coincident GetRouteLength stays 0"),
		Route->GetRouteLength(),
		0.f);
	return ExpectConstantSample(*this, *Route, SharedLocation);
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardRouteRuntimeSampleClampsPastEndsTest,
	"Skyguard52.Route.Runtime.SampleClampsNegativeAndHugeDistance",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardRouteRuntimeSampleClampsPastEndsTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardRouteRuntimeFailClosedTests;

	USkyguardRouteRuntime* Route = MakeRuntime();
	TestNotNull(TEXT("two-point route runtime is created"), Route);
	if (!Route)
	{
		return false;
	}

	const FVector StartLocation(0.f, 0.f, 80.f);
	const FVector EndLocation(2500.f, 0.f, 80.f);
	const FSkyguardRouteDefinition Definition = MakeDefinition(
		TEXT("TwoPointRoute"),
		{
			MakePoint(TEXT("Start"), StartLocation),
			MakePoint(TEXT("End"), EndLocation)
		});
	TestTrue(TEXT("two-point route initializes"), Route->InitializeRoute(Definition));
	TestEqual(
		TEXT("two-point GetRouteLength is the segment"),
		Route->GetRouteLength(),
		FVector::Distance(StartLocation, EndLocation));
	TestTrue(
		TEXT("SampleLocationByDistance(-100) clamps to start"),
		Route->SampleLocationByDistance(-100.f).Equals(StartLocation, 0.01f));
	TestTrue(
		TEXT("SampleLocationByDistance(1e9) clamps to end"),
		Route->SampleLocationByDistance(1.0e9f).Equals(EndLocation, 0.01f));
	return true;
}

#endif
