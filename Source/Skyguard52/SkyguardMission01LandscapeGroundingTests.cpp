#if WITH_DEV_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "SkyguardMission01LandscapeGroundingLibrary.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardLandscapeGroundingNullLandscapeTest,
	"Skyguard.Mission01.Environment.Grounding.NullLandscapeFailsClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardLandscapeGroundingNullLandscapeTest::RunTest(
	const FString& Parameters)
{
	const FSkyguardLandscapeHeightSample Result =
		USkyguardMission01LandscapeGroundingLibrary::SampleLandscapeHeight(
			nullptr,
			FVector::ZeroVector);
	TestFalse(TEXT("Null Landscape cannot produce a valid sample"), Result.bValid);
	TestTrue(TEXT("Null Landscape records an error"), !Result.Error.IsEmpty());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardLandscapeGroundingFootprintContractTest,
	"Skyguard.Mission01.Environment.Grounding.FootprintCountsAreGoverned",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardLandscapeGroundingFootprintContractTest::RunTest(
	const FString& Parameters)
{
	const TArray<FVector> InvalidCount = {
		FVector(0.f, 0.f, 0.f),
		FVector(100.f, 0.f, 0.f),
		FVector(0.f, 100.f, 0.f)};
	const FSkyguardLandscapeFootprintSampleResult Result =
		USkyguardMission01LandscapeGroundingLibrary::SampleLandscapeFootprint(
			nullptr,
			InvalidCount);
	TestFalse(TEXT("Invalid input cannot pass"), Result.bSuccess);
	TestEqual(TEXT("Requested sample count is preserved"),
		Result.RequiredSampleCount, InvalidCount.Num());
	TestEqual(TEXT("Invalid count records the governed error"), Result.Error,
		FString(TEXT("Footprints require exactly 5, 9, or 13 samples.")));
	return true;
}

#endif
