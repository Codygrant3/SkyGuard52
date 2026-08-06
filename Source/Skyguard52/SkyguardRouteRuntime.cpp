#include "SkyguardRouteRuntime.h"

bool USkyguardRouteRuntime::InitializeRoute(const FSkyguardRouteDefinition& Definition)
{
	Route = Definition;
	CumulativeDistances.Reset();
	TotalLength = 0.f;
	if (Route.Points.Num() < 2)
	{
		return false;
	}

	CumulativeDistances.Add(0.f);
	for (int32 Index = 1; Index < Route.Points.Num(); ++Index)
	{
		TotalLength += FVector::Distance(
			Route.Points[Index - 1].WorldLocation,
			Route.Points[Index].WorldLocation);
		CumulativeDistances.Add(TotalLength);
	}
	return TotalLength > KINDA_SMALL_NUMBER;
}

FVector USkyguardRouteRuntime::SampleLocationByDistance(const float DistanceCentimeters) const
{
	if (Route.Points.IsEmpty())
	{
		return FVector::ZeroVector;
	}
	if (Route.Points.Num() == 1 || TotalLength <= KINDA_SMALL_NUMBER)
	{
		return Route.Points[0].WorldLocation;
	}

	const float ClampedDistance = FMath::Clamp(DistanceCentimeters, 0.f, TotalLength);
	for (int32 Index = 1; Index < CumulativeDistances.Num(); ++Index)
	{
		if (ClampedDistance <= CumulativeDistances[Index])
		{
			const float SegmentStart = CumulativeDistances[Index - 1];
			const float SegmentLength = CumulativeDistances[Index] - SegmentStart;
			const float Alpha =
				SegmentLength > KINDA_SMALL_NUMBER
					? (ClampedDistance - SegmentStart) / SegmentLength
					: 0.f;
			return FMath::Lerp(
				Route.Points[Index - 1].WorldLocation,
				Route.Points[Index].WorldLocation,
				Alpha);
		}
	}
	return Route.Points.Last().WorldLocation;
}
