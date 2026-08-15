#include "SkyguardAudioProductionBank.h"

#include "Sound/SoundSubmix.h"

namespace
{
	FName CategoryName(const ESkyguardProductionAudioCategory Category)
	{
		const UEnum* Enum = StaticEnum<ESkyguardProductionAudioCategory>();
		return Enum ? FName(*Enum->GetNameStringByValue(static_cast<int64>(Category))) : NAME_None;
	}

	template<typename TObjectType>
	bool HasSoftReference(const TSoftObjectPtr<TObjectType>& Value)
	{
		// Structural validation only needs a governed soft-object path. Calling
		// Get() here would require every routing type to be fully defined and
		// would also turn validation into an unintended synchronous-load check.
		return !Value.IsNull();
	}
}

const TArray<ESkyguardProductionAudioCategory>& USkyguardAudioProductionBank::GetRequiredCategories()
{
	static const TArray<ESkyguardProductionAudioCategory> Categories = {
		ESkyguardProductionAudioCategory::EngineIdle,
		ESkyguardProductionAudioCategory::EngineCruise,
		ESkyguardProductionAudioCategory::EnginePower,
		ESkyguardProductionAudioCategory::Propeller,
		ESkyguardProductionAudioCategory::OpenCockpitWind,
		ESkyguardProductionAudioCategory::RifleMuzzle,
		ESkyguardProductionAudioCategory::RifleMechanical,
		ESkyguardProductionAudioCategory::RifleCasing,
		ESkyguardProductionAudioCategory::RifleReflection,
		ESkyguardProductionAudioCategory::IglaSearch,
		ESkyguardProductionAudioCategory::IglaLock,
		ESkyguardProductionAudioCategory::IglaLaunch,
		ESkyguardProductionAudioCategory::IglaFlyby,
		ESkyguardProductionAudioCategory::IglaImpact,
		ESkyguardProductionAudioCategory::DroneLightMotor,
		ESkyguardProductionAudioCategory::DroneHeavyMotor,
		ESkyguardProductionAudioCategory::DroneFlyby,
		ESkyguardProductionAudioCategory::ExplosionSmallCrack,
		ESkyguardProductionAudioCategory::ExplosionSmallBody,
		ESkyguardProductionAudioCategory::ExplosionSmallDebris,
		ESkyguardProductionAudioCategory::ExplosionSmallTail,
		ESkyguardProductionAudioCategory::ExplosionHeavyCrack,
		ESkyguardProductionAudioCategory::ExplosionHeavyBody,
		ESkyguardProductionAudioCategory::ExplosionHeavyDebris,
		ESkyguardProductionAudioCategory::ExplosionHeavyTail,
	};
	return Categories;
}

FText USkyguardAudioProductionBank::GetCategoryDisplayName(
	const ESkyguardProductionAudioCategory Category)
{
	switch (Category)
	{
	case ESkyguardProductionAudioCategory::EngineIdle:
		return FText::FromString(TEXT("Engine Idle"));
	case ESkyguardProductionAudioCategory::EngineCruise:
		return FText::FromString(TEXT("Engine Cruise"));
	case ESkyguardProductionAudioCategory::EnginePower:
		return FText::FromString(TEXT("Engine Power"));
	case ESkyguardProductionAudioCategory::Propeller:
		return FText::FromString(TEXT("Propeller"));
	case ESkyguardProductionAudioCategory::OpenCockpitWind:
		return FText::FromString(TEXT("Open Cockpit Wind"));
	case ESkyguardProductionAudioCategory::RifleMuzzle:
		return FText::FromString(TEXT("Rifle Muzzle"));
	case ESkyguardProductionAudioCategory::RifleMechanical:
		return FText::FromString(TEXT("Rifle Mechanical"));
	case ESkyguardProductionAudioCategory::RifleCasing:
		return FText::FromString(TEXT("Rifle Casing"));
	case ESkyguardProductionAudioCategory::RifleReflection:
		return FText::FromString(TEXT("Rifle Reflection"));
	case ESkyguardProductionAudioCategory::IglaSearch:
		return FText::FromString(TEXT("Igla Search"));
	case ESkyguardProductionAudioCategory::IglaLock:
		return FText::FromString(TEXT("Igla Lock"));
	case ESkyguardProductionAudioCategory::IglaLaunch:
		return FText::FromString(TEXT("Igla Launch"));
	case ESkyguardProductionAudioCategory::IglaFlyby:
		return FText::FromString(TEXT("Igla Flyby"));
	case ESkyguardProductionAudioCategory::IglaImpact:
		return FText::FromString(TEXT("Igla Impact"));
	case ESkyguardProductionAudioCategory::DroneLightMotor:
		return FText::FromString(TEXT("Drone Light Motor"));
	case ESkyguardProductionAudioCategory::DroneHeavyMotor:
		return FText::FromString(TEXT("Drone Heavy Motor"));
	case ESkyguardProductionAudioCategory::DroneFlyby:
		return FText::FromString(TEXT("Drone Flyby"));
	case ESkyguardProductionAudioCategory::ExplosionSmallCrack:
		return FText::FromString(TEXT("Explosion Small Crack"));
	case ESkyguardProductionAudioCategory::ExplosionSmallBody:
		return FText::FromString(TEXT("Explosion Small Body"));
	case ESkyguardProductionAudioCategory::ExplosionSmallDebris:
		return FText::FromString(TEXT("Explosion Small Debris"));
	case ESkyguardProductionAudioCategory::ExplosionSmallTail:
		return FText::FromString(TEXT("Explosion Small Tail"));
	case ESkyguardProductionAudioCategory::ExplosionHeavyCrack:
		return FText::FromString(TEXT("Explosion Heavy Crack"));
	case ESkyguardProductionAudioCategory::ExplosionHeavyBody:
		return FText::FromString(TEXT("Explosion Heavy Body"));
	case ESkyguardProductionAudioCategory::ExplosionHeavyDebris:
		return FText::FromString(TEXT("Explosion Heavy Debris"));
	case ESkyguardProductionAudioCategory::ExplosionHeavyTail:
		return FText::FromString(TEXT("Explosion Heavy Tail"));
	default:
		return FText::FromString(TEXT("Unknown Audio Category"));
	}
}

void USkyguardAudioProductionBank::InitializeRequiredEntries()
{
	Entries.Reset();
	EnsureDefaultEntries();
}

void USkyguardAudioProductionBank::EnsureDefaultEntries()
{
	for (const ESkyguardProductionAudioCategory Category : GetRequiredCategories())
	{
		if (FSkyguardProductionAudioEntry* Existing =
			Entries.FindByPredicate([Category](const FSkyguardProductionAudioEntry& Entry)
			{
				return Entry.Category == Category;
			}))
		{
			if (Existing->DisplayName.IsEmpty())
			{
				Existing->DisplayName = GetCategoryDisplayName(Category);
			}
			continue;
		}

		FSkyguardProductionAudioEntry& Entry = Entries.AddDefaulted_GetRef();
		Entry.Category = Category;
		Entry.DisplayName = GetCategoryDisplayName(Category);
		Entry.SourceStatus = ESkyguardAudioSourceStatus::MISSING_SOURCE;
		Entry.Sound.Reset();
		Entry.Attenuation.Reset();
		Entry.Concurrency.Reset();
		Entry.OutputSubmix.Reset();
		Entry.ProvenanceId = NAME_None;
		Entry.SourceSha256.Reset();
	}
}

TArray<ESkyguardProductionAudioCategory>
USkyguardAudioProductionBank::GetUnboundRequiredCategories() const
{
	TArray<ESkyguardProductionAudioCategory> Unbound;
	for (const ESkyguardProductionAudioCategory Category : GetRequiredCategories())
	{
		const FSkyguardProductionAudioEntry* Entry = FindEntry(Category);
		const bool bBound = Entry && HasBoundObject(Entry->Sound);
		if (!bBound)
		{
			Unbound.Add(Category);
		}
	}
	return Unbound;
}

const FSkyguardProductionAudioEntry* USkyguardAudioProductionBank::FindEntry(
	const ESkyguardProductionAudioCategory Category) const
{
	return Entries.FindByPredicate([Category](const FSkyguardProductionAudioEntry& Entry)
	{
		return Entry.Category == Category;
	});
}

bool USkyguardAudioProductionBank::HasBoundObject(const TSoftObjectPtr<USoundBase>& Value)
{
	return HasSoftReference(Value);
}

bool USkyguardAudioProductionBank::HasValidSha256(const FString& Value)
{
	if (Value.Len() != 64)
	{
		return false;
	}
	for (const TCHAR Character : Value)
	{
		if (!FChar::IsHexDigit(Character))
		{
			return false;
		}
	}
	return true;
}

FSkyguardProductionAudioAudit USkyguardAudioProductionBank::EvaluateReadiness() const
{
	FSkyguardProductionAudioAudit Audit;
	Audit.RequiredCategoryCount = GetRequiredCategories().Num();

	for (const ESkyguardProductionAudioCategory Category : GetRequiredCategories())
	{
		int32 DuplicateCount = 0;
		for (const FSkyguardProductionAudioEntry& Candidate : Entries)
		{
			DuplicateCount += Candidate.Category == Category ? 1 : 0;
		}
		if (DuplicateCount != 1)
		{
			Audit.MissingCategoryEntries.Add(CategoryName(Category));
			continue;
		}

		const FSkyguardProductionAudioEntry* Entry = FindEntry(Category);
		const bool bHasSound = Entry && HasBoundObject(Entry->Sound);
		if (Entry->SourceStatus == ESkyguardAudioSourceStatus::MISSING_SOURCE)
		{
			if (bHasSound)
			{
				Audit.InvalidSourceEntries.Add(CategoryName(Category));
			}
			else
			{
				++Audit.ExplicitMissingSourceCount;
			}
			continue;
		}
		if (Entry->SourceStatus == ESkyguardAudioSourceStatus::PROCEDURAL_QA_TEST_ONLY)
		{
			++Audit.QATestOnlyCount;
			if (!bHasSound)
			{
				Audit.InvalidSourceEntries.Add(CategoryName(Category));
			}
			continue;
		}
		if (!bHasSound || Entry->ProvenanceId.IsNone() || !HasValidSha256(Entry->SourceSha256))
		{
			Audit.InvalidSourceEntries.Add(CategoryName(Category));
			continue;
		}
		if (!HasSoftReference(Entry->Sound))
		{
			Audit.MissingSoundBindings.Add(CategoryName(Category));
		}
		if (!HasSoftReference(Entry->Attenuation))
		{
			Audit.MissingAttenuationBindings.Add(CategoryName(Category));
		}
		if (!HasSoftReference(Entry->Concurrency))
		{
			Audit.MissingConcurrencyBindings.Add(CategoryName(Category));
		}
		if (!HasSoftReference(Entry->OutputSubmix))
		{
			Audit.MissingOutputSubmixBindings.Add(CategoryName(Category));
		}
		++Audit.BoundProductionSourceCount;
	}

	auto RequireRouting = [&Audit](const bool bPresent, const TCHAR* Name)
	{
		if (!bPresent)
		{
			Audit.MissingRoutingAssets.Add(FName(Name));
		}
	};
	RequireRouting(HasSoftReference(Routing.MasterSubmix), TEXT("MasterSubmix"));
	RequireRouting(HasSoftReference(Routing.CockpitSubmix), TEXT("CockpitSubmix"));
	RequireRouting(HasSoftReference(Routing.ExteriorSubmix), TEXT("ExteriorSubmix"));
	RequireRouting(HasSoftReference(Routing.WeaponsSubmix), TEXT("WeaponsSubmix"));
	RequireRouting(HasSoftReference(Routing.ExplosionsSubmix), TEXT("ExplosionsSubmix"));
	RequireRouting(HasSoftReference(Routing.RadioSubmix), TEXT("RadioSubmix"));
	RequireRouting(HasSoftReference(Routing.CockpitSoundMix), TEXT("CockpitSoundMix"));

	Audit.bCategoryContractComplete =
		Audit.MissingCategoryEntries.IsEmpty()
		&& Audit.InvalidSourceEntries.IsEmpty()
		&& Audit.BoundProductionSourceCount + Audit.ExplicitMissingSourceCount + Audit.QATestOnlyCount
			== Audit.RequiredCategoryCount;
	Audit.bProductionReady =
		Audit.bCategoryContractComplete
		&& Audit.BoundProductionSourceCount == Audit.RequiredCategoryCount
		&& Audit.QATestOnlyCount == 0
		&& Audit.ExplicitMissingSourceCount == 0
		&& Audit.MissingSoundBindings.IsEmpty()
		&& Audit.MissingAttenuationBindings.IsEmpty()
		&& Audit.MissingConcurrencyBindings.IsEmpty()
		&& Audit.MissingOutputSubmixBindings.IsEmpty()
		&& Audit.MissingRoutingAssets.IsEmpty();
	return Audit;
}

bool USkyguardAudioProductionBank::ConfigureRoutingTopology()
{
	USoundSubmixBase* Master = Routing.MasterSubmix.LoadSynchronous();
	if (!Master)
	{
		return false;
	}

	const TSoftObjectPtr<USoundSubmixBase> Children[] = {
		Routing.CockpitSubmix,
		Routing.ExteriorSubmix,
		Routing.WeaponsSubmix,
		Routing.ExplosionsSubmix,
		Routing.RadioSubmix,
	};

	for (const TSoftObjectPtr<USoundSubmixBase>& ChildReference : Children)
	{
		USoundSubmixWithParentBase* Child =
			Cast<USoundSubmixWithParentBase>(ChildReference.LoadSynchronous());
		if (!Child)
		{
			return false;
		}
		Child->SetParentSubmix(Master);
		Child->MarkPackageDirty();
	}

	Master->MarkPackageDirty();
	return true;
}
