#include "SkyguardMissionMapAssemblyDirector.h"

#include "Components/SceneComponent.h"
#include "Components/SplineComponent.h"
#include "SkyguardMissionDefinition.h"

ASkyguardMissionMapAssemblyDirector::ASkyguardMissionMapAssemblyDirector()
{
	PrimaryActorTick.bCanEverTick = false;
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("MissionMapAssemblyRoot"));
	SetRootComponent(Root);
	FlightRouteSpline = CreateDefaultSubobject<USplineComponent>(TEXT("FlightRouteSpline"));
	FlightRouteSpline->SetupAttachment(Root);
	FlightRouteSpline->SetClosedLoop(false);
	Tags.AddUnique(TEXT("Skyguard.MissionMap.AssemblyDirector"));
}

void ASkyguardMissionMapAssemblyDirector::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	RebuildRouteSpline();
	TArray<FText> IgnoredErrors;
	ValidateAssembly(IgnoredErrors);
}

void ASkyguardMissionMapAssemblyDirector::RebuildRouteSpline()
{
	if (!FlightRouteSpline)
	{
		return;
	}
	FlightRouteSpline->ClearSplinePoints(false);
	for (const FVector& RoutePoint : RoutePoints)
	{
		FlightRouteSpline->AddSplinePoint(
			GetActorTransform().InverseTransformPosition(RoutePoint),
			ESplineCoordinateSpace::Local,
			false);
	}
	FlightRouteSpline->UpdateSpline();
}

float ASkyguardMissionMapAssemblyDirector::CalculateRouteLength() const
{
	float Length = 0.f;
	for (int32 Index = 1; Index < RoutePoints.Num(); ++Index)
	{
		Length += FVector::Distance(RoutePoints[Index - 1], RoutePoints[Index]);
	}
	return Length;
}

bool ASkyguardMissionMapAssemblyDirector::ValidateAssembly(TArray<FText>& OutErrors)
{
	OutErrors.Reset();
	auto AddError = [&OutErrors](const FString& Error)
	{
		OutErrors.Add(FText::FromString(Error));
	};

	Readiness = FSkyguardMissionMapReadiness();
	Readiness.RoutePointCount = RoutePoints.Num();
	Readiness.ObjectiveAnchorCount = ObjectiveAnchors.Num();
	Readiness.LandmarkCount = LandmarkAnchors.Num();
	Readiness.RouteLengthCentimeters = CalculateRouteLength();

	TArray<FText> DefinitionErrors;
	Readiness.bDefinitionValid =
		MissionDefinition &&
		MissionDefinition->MissionId == MissionId &&
		MissionDefinition->ValidateDefinition(DefinitionErrors);
	if (!MissionDefinition)
	{
		AddError(TEXT("MissionDefinition is required."));
	}
	else
	{
		if (MissionDefinition->MissionId != MissionId)
		{
			AddError(TEXT("Director MissionId does not match MissionDefinition."));
		}
		for (const FText& DefinitionError : DefinitionErrors)
		{
			AddError(FString::Printf(
				TEXT("MissionDefinition: %s"),
				*DefinitionError.ToString()));
		}
	}

	Readiness.bRouteMatchesDefinition =
		MissionDefinition &&
		RoutePoints.Num() == MissionDefinition->Route.Points.Num() &&
		RoutePoints.Num() >= 4 &&
		Readiness.RouteLengthCentimeters >= 30000.f;
	if (Readiness.bRouteMatchesDefinition)
	{
		for (int32 Index = 0; Index < RoutePoints.Num(); ++Index)
		{
			if (!RoutePoints[Index].Equals(
				MissionDefinition->Route.Points[Index].WorldLocation,
				1.f))
			{
				Readiness.bRouteMatchesDefinition = false;
				break;
			}
		}
	}
	if (!Readiness.bRouteMatchesDefinition)
	{
		AddError(TEXT("Map route must match the validated mission definition and span at least 300 metres."));
	}

	TSet<FName> AnchoredObjectiveIds;
	bool bObjectiveIdsValid = true;
	for (const FSkyguardMissionObjectiveAnchor& Anchor : ObjectiveAnchors)
	{
		if (Anchor.ObjectiveId.IsNone() ||
			AnchoredObjectiveIds.Contains(Anchor.ObjectiveId) ||
			!MissionDefinition ||
			!MissionDefinition->FindObjective(Anchor.ObjectiveId))
		{
			bObjectiveIdsValid = false;
		}
		AnchoredObjectiveIds.Add(Anchor.ObjectiveId);
	}
	Readiness.bRequiredObjectivesAnchored =
		MissionDefinition && bObjectiveIdsValid;
	if (MissionDefinition && Readiness.bRequiredObjectivesAnchored)
	{
		for (const FSkyguardObjectiveDefinition& Objective : MissionDefinition->Objectives)
		{
			if (Objective.bRequiredForMissionSuccess &&
				!AnchoredObjectiveIds.Contains(Objective.ObjectiveId))
			{
				Readiness.bRequiredObjectivesAnchored = false;
				break;
			}
		}
	}
	if (!Readiness.bRequiredObjectivesAnchored)
	{
		AddError(TEXT("Every required objective needs one valid, unique map anchor."));
	}

	Readiness.bWeatherMatchesDefinition =
		MissionDefinition &&
		!WeatherProfileId.IsNone() &&
		WeatherProfileId == MissionDefinition->Weather.ProfileId;
	if (!Readiness.bWeatherMatchesDefinition)
	{
		AddError(TEXT("Map weather profile must match the mission definition."));
	}

	TSet<FName> LandmarkIds;
	TSet<FName> LandmarkRoles;
	for (const FSkyguardMissionLandmarkAnchor& Landmark : LandmarkAnchors)
	{
		if (Landmark.bMissionExclusive)
		{
			++Readiness.MissionExclusiveLandmarkCount;
		}
		LandmarkIds.Add(Landmark.LandmarkId);
		LandmarkRoles.Add(Landmark.Role);
	}
	Readiness.bLandmarksDistinct =
		LandmarkAnchors.Num() >= 3 &&
		LandmarkIds.Num() == LandmarkAnchors.Num() &&
		LandmarkRoles.Num() >= 3 &&
		Readiness.MissionExclusiveLandmarkCount >= 2;
	if (!Readiness.bLandmarksDistinct)
	{
		AddError(TEXT("Map needs three unique landmark roles and at least two mission-exclusive landmarks."));
	}

	return OutErrors.IsEmpty();
}

bool ASkyguardMissionMapAssemblyDirector::IsPointInsideFlightClearance(
	const FVector& WorldPoint) const
{
	if (RoutePoints.Num() < 2)
	{
		return false;
	}
	for (int32 Index = 1; Index < RoutePoints.Num(); ++Index)
	{
		const FVector Start = RoutePoints[Index - 1];
		const FVector End = RoutePoints[Index];
		const FVector Closest = FMath::ClosestPointOnSegment(WorldPoint, Start, End);
		const FVector Delta = WorldPoint - Closest;
		if (FMath::Abs(Delta.Z) <= FlightClearanceVerticalCentimeters &&
			FVector2D(Delta.X, Delta.Y).Size() <= FlightClearanceRadiusCentimeters)
		{
			return true;
		}
	}
	return false;
}
