#include "SkyguardMissionDefinition.h"

#include "Engine/World.h"

FPrimaryAssetId USkyguardMissionDefinition::GetPrimaryAssetId() const
{
	return FPrimaryAssetId(TEXT("SkyguardMission"), MissionId.IsNone() ? GetFName() : MissionId);
}

const FSkyguardObjectiveDefinition* USkyguardMissionDefinition::FindObjective(const FName ObjectiveId) const
{
	return Objectives.FindByPredicate(
		[ObjectiveId](const FSkyguardObjectiveDefinition& Objective)
		{
			return Objective.ObjectiveId == ObjectiveId;
		});
}

bool USkyguardMissionDefinition::ValidateDefinition(TArray<FText>& OutErrors) const
{
	OutErrors.Reset();
	auto AddError = [&OutErrors](const FString& Error)
	{
		OutErrors.Add(FText::FromString(Error));
	};

	if (MissionId.IsNone())
	{
		AddError(TEXT("MissionId must be set."));
	}
	if (DisplayName.IsEmpty())
	{
		AddError(TEXT("DisplayName must be set."));
	}
	if (CampaignOrder < 1)
	{
		AddError(TEXT("CampaignOrder must be at least one."));
	}
	if (Route.RouteId.IsNone() || Route.Points.Num() < 2)
	{
		AddError(TEXT("Route requires an id and at least two points."));
	}

	TSet<FName> RoutePointIds;
	for (const FSkyguardRoutePoint& Point : Route.Points)
	{
		if (Point.PointId.IsNone() || RoutePointIds.Contains(Point.PointId))
		{
			AddError(TEXT("Route point ids must be set and unique."));
		}
		RoutePointIds.Add(Point.PointId);
		if (Point.TargetAirspeedKph <= 0.f)
		{
			AddError(TEXT("Route point airspeed must be positive."));
		}
	}

	TSet<FName> ObjectiveIds;
	bool bHasRequiredObjective = false;
	for (const FSkyguardObjectiveDefinition& Objective : Objectives)
	{
		if (Objective.ObjectiveId.IsNone() || ObjectiveIds.Contains(Objective.ObjectiveId))
		{
			AddError(TEXT("Objective ids must be set and unique."));
		}
		ObjectiveIds.Add(Objective.ObjectiveId);
		bHasRequiredObjective |= Objective.bRequiredForMissionSuccess;
		if (Objective.RequiredProgress < 1)
		{
			AddError(TEXT("Objective RequiredProgress must be at least one."));
		}
	}
	if (!bHasRequiredObjective)
	{
		AddError(TEXT("At least one required objective is needed."));
	}

	TSet<FName> WaveIds;
	for (const FSkyguardEnemyWaveDefinition& Wave : Waves)
	{
		if (Wave.WaveId.IsNone() || WaveIds.Contains(Wave.WaveId))
		{
			AddError(TEXT("Wave ids must be set and unique."));
		}
		WaveIds.Add(Wave.WaveId);
		if (!Wave.CompletionObjectiveId.IsNone() && !ObjectiveIds.Contains(Wave.CompletionObjectiveId))
		{
			AddError(FString::Printf(
				TEXT("Wave %s references an unknown completion objective."),
				*Wave.WaveId.ToString()));
		}
		for (const FSkyguardEnemyFormationDefinition& Formation : Wave.Formations)
		{
			if (Formation.FormationId.IsNone() || Formation.UnitCount < 1 || Formation.UnitCount > 32)
			{
				AddError(TEXT("Every formation needs an id and one to thirty-two units."));
			}
		}
	}

	if (!Boss.BossId.IsNone())
	{
		if (Boss.MaximumBreakupPieces < 0 || Boss.MaximumBreakupPieces > 12)
		{
			AddError(TEXT("Boss breakup budget must remain between zero and twelve."));
		}
		if (!Boss.DefeatObjectiveId.IsNone() && !ObjectiveIds.Contains(Boss.DefeatObjectiveId))
		{
			AddError(TEXT("Boss defeat objective must reference a mission objective."));
		}
		TSet<FName> WeakPointIds;
		for (const FSkyguardBossWeakPointDefinition& WeakPoint : Boss.WeakPoints)
		{
			if (WeakPoint.WeakPointId.IsNone() || WeakPointIds.Contains(WeakPoint.WeakPointId))
			{
				AddError(TEXT("Boss weak-point ids must be set and unique."));
			}
			if (WeakPoint.RequiredWeapon.IsNone())
			{
				AddError(TEXT("Every boss weak point requires an authored weapon id."));
			}
			WeakPointIds.Add(WeakPoint.WeakPointId);
		}
		for (const FSkyguardBossWeakPointDefinition& WeakPoint : Boss.WeakPoints)
		{
			if (!WeakPoint.ExposesWeakPointId.IsNone() &&
				!WeakPointIds.Contains(WeakPoint.ExposesWeakPointId))
			{
				AddError(TEXT("Boss weak-point exposure links must resolve inside the boss definition."));
			}
		}
	}

	if (Weather.TimeOfDayHours < 0.f || Weather.TimeOfDayHours > 24.f ||
		Weather.Precipitation < 0.f || Weather.Precipitation > 1.f ||
		Weather.CloudCoverage < 0.f || Weather.CloudCoverage > 1.f)
	{
		AddError(TEXT("Weather values are outside their authored ranges."));
	}
	if (ScoreRules.BronzeThreshold > ScoreRules.SilverThreshold ||
		ScoreRules.SilverThreshold > ScoreRules.GoldThreshold)
	{
		AddError(TEXT("Medal score thresholds must be monotonic."));
	}

	return OutErrors.IsEmpty();
}
