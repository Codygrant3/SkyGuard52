#include "SkyguardCampaignDefinition.h"

#include "SkyguardMissionDefinition.h"

FPrimaryAssetId USkyguardCampaignDefinition::GetPrimaryAssetId() const
{
	return FPrimaryAssetId(TEXT("SkyguardCampaign"), CampaignId.IsNone() ? GetFName() : CampaignId);
}

USkyguardMissionDefinition* USkyguardCampaignDefinition::FindMission(const FName MissionId) const
{
	const TObjectPtr<USkyguardMissionDefinition>* Found = Missions.FindByPredicate(
		[MissionId](const TObjectPtr<USkyguardMissionDefinition>& Mission)
		{
			return Mission && Mission->MissionId == MissionId;
		});
	return Found ? Found->Get() : nullptr;
}

bool USkyguardCampaignDefinition::ValidateDefinition(TArray<FText>& OutErrors) const
{
	OutErrors.Reset();
	auto AddError = [&OutErrors](const FString& Error)
	{
		OutErrors.Add(FText::FromString(Error));
	};

	if (CampaignId.IsNone())
	{
		AddError(TEXT("CampaignId must be set."));
	}
	if (Missions.IsEmpty())
	{
		AddError(TEXT("Campaign requires at least one mission."));
		return false;
	}

	TMap<FName, int32> MissionOrderById;
	TSet<int32> UsedOrders;
	for (const USkyguardMissionDefinition* Mission : Missions)
	{
		if (!Mission)
		{
			AddError(TEXT("Campaign contains a null mission definition."));
			continue;
		}
		if (MissionOrderById.Contains(Mission->MissionId))
		{
			AddError(TEXT("Campaign mission ids must be unique."));
		}
		MissionOrderById.Add(Mission->MissionId, Mission->CampaignOrder);
		if (UsedOrders.Contains(Mission->CampaignOrder))
		{
			AddError(TEXT("Campaign order values must be unique."));
		}
		UsedOrders.Add(Mission->CampaignOrder);

		TArray<FText> MissionErrors;
		if (!Mission->ValidateDefinition(MissionErrors))
		{
			for (const FText& MissionError : MissionErrors)
			{
				AddError(FString::Printf(
					TEXT("%s: %s"),
					*Mission->MissionId.ToString(),
					*MissionError.ToString()));
			}
		}
	}

	for (const USkyguardMissionDefinition* Mission : Missions)
	{
		if (!Mission)
		{
			continue;
		}
		TSet<FName> UniquePrerequisites;
		for (const FName PrerequisiteId : Mission->PrerequisiteMissionIds)
		{
			if (UniquePrerequisites.Contains(PrerequisiteId))
			{
				AddError(FString::Printf(
					TEXT("%s contains duplicate prerequisite %s."),
					*Mission->MissionId.ToString(),
					*PrerequisiteId.ToString()));
			}
			UniquePrerequisites.Add(PrerequisiteId);
			const int32* PrerequisiteOrder = MissionOrderById.Find(PrerequisiteId);
			if (!PrerequisiteOrder)
			{
				AddError(FString::Printf(
					TEXT("%s references unknown prerequisite %s."),
					*Mission->MissionId.ToString(),
					*PrerequisiteId.ToString()));
			}
			else if (*PrerequisiteOrder >= Mission->CampaignOrder)
			{
				AddError(FString::Printf(
					TEXT("%s prerequisite %s must occur earlier in campaign order."),
					*Mission->MissionId.ToString(),
					*PrerequisiteId.ToString()));
			}
		}
	}

	return OutErrors.IsEmpty();
}
