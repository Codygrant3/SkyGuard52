#include "SkyguardMission01LandscapeGroundingLibrary.h"

#include "LandscapeHeightfieldCollisionComponent.h"
#include "LandscapeProxy.h"

namespace
{
	constexpr float DuplicateXYToleranceCentimeters = 0.01f;

	bool IsPermittedFootprintCount(const int32 Count)
	{
		return Count == 5 || Count == 9 || Count == 13;
	}

	FString GovernedHeightfieldSourceName()
	{
#if WITH_EDITOR
		return TEXT("Editor");
#else
		return TEXT("Complex");
#endif
	}
}

FSkyguardLandscapeHeightSample
USkyguardMission01LandscapeGroundingLibrary::SampleLandscapeHeight(
	ALandscapeProxy* Landscape,
	const FVector& WorldLocation)
{
	FSkyguardLandscapeHeightSample Result;
	Result.QueryLocation = WorldLocation;
	Result.HeightfieldSource = GovernedHeightfieldSourceName();

	if (!IsValid(Landscape))
	{
		Result.Error = TEXT("A valid Landscape proxy is required.");
		return Result;
	}
	if (WorldLocation.ContainsNaN())
	{
		Result.Error = TEXT("The world-space query location must be finite.");
		return Result;
	}

#if WITH_EDITOR
	const TOptional<float> Height = Landscape->GetHeightAtLocation(
		WorldLocation,
		EHeightfieldSource::Editor);
#else
	const TOptional<float> Height = Landscape->GetHeightAtLocation(
		WorldLocation,
		EHeightfieldSource::Complex);
#endif

	if (!Height.IsSet() || !FMath::IsFinite(Height.GetValue()))
	{
		Result.Error = TEXT("The Landscape does not support this XY location.");
		return Result;
	}

	Result.bValid = true;
	Result.HeightCentimeters = Height.GetValue();
	return Result;
}

FSkyguardLandscapeFootprintSampleResult
USkyguardMission01LandscapeGroundingLibrary::SampleLandscapeFootprint(
	ALandscapeProxy* Landscape,
	const TArray<FVector>& WorldLocations)
{
	FSkyguardLandscapeFootprintSampleResult Result;
	Result.RequiredSampleCount = WorldLocations.Num();

	if (!IsPermittedFootprintCount(WorldLocations.Num()))
	{
		Result.Error = TEXT("Footprints require exactly 5, 9, or 13 samples.");
		return Result;
	}
	if (!IsValid(Landscape))
	{
		Result.Error = TEXT("A valid Landscape proxy is required.");
		return Result;
	}

	TArray<FVector2D> SeenXY;
	SeenXY.Reserve(WorldLocations.Num());
	for (const FVector& Location : WorldLocations)
	{
		if (Location.ContainsNaN())
		{
			Result.Error = TEXT("Every footprint query location must be finite.");
			return Result;
		}
		const FVector2D XY(Location.X, Location.Y);
		for (const FVector2D& Existing : SeenXY)
		{
			if (FVector2D::Distance(XY, Existing)
				<= DuplicateXYToleranceCentimeters)
			{
				Result.Error = TEXT("Every footprint sample XY location must be unique.");
				return Result;
			}
		}
		SeenXY.Add(XY);
	}

	Result.Samples.Reserve(WorldLocations.Num());
	float Minimum = MAX_flt;
	float Maximum = -MAX_flt;
	double Sum = 0.0;
	for (const FVector& Location : WorldLocations)
	{
		FSkyguardLandscapeHeightSample Sample =
			SampleLandscapeHeight(Landscape, Location);
		if (Sample.bValid)
		{
			++Result.ValidSampleCount;
			Minimum = FMath::Min(Minimum, Sample.HeightCentimeters);
			Maximum = FMath::Max(Maximum, Sample.HeightCentimeters);
			Sum += static_cast<double>(Sample.HeightCentimeters);
		}
		Result.Samples.Add(MoveTemp(Sample));
	}

	Result.SupportedFraction = static_cast<float>(Result.ValidSampleCount)
		/ static_cast<float>(Result.RequiredSampleCount);
	if (Result.ValidSampleCount != Result.RequiredSampleCount)
	{
		Result.Error = FString::Printf(
			TEXT("Landscape support is incomplete: %d/%d samples."),
			Result.ValidSampleCount,
			Result.RequiredSampleCount);
		return Result;
	}

	Result.MinimumHeightCentimeters = Minimum;
	Result.MaximumHeightCentimeters = Maximum;
	Result.MeanHeightCentimeters =
		static_cast<float>(Sum / static_cast<double>(Result.ValidSampleCount));
	Result.HeightDeltaCentimeters = Maximum - Minimum;
	Result.bSuccess = true;
	return Result;
}
