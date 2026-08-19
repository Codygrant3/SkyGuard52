#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignRoster.h"
#include "SkyguardCampaignTheaterKit.h"
#include "SkyguardCpgDebrief.h"
#include "SkyguardGunshipSortieDirector.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Misc/AutomationTest.h"

namespace SkyguardCampaignTheaterKitTests
{
	bool CopyHasBannedTerm(const FString& Text)
	{
		return SkyguardCpgCopyHasBannedTerm(Text);
	}

	ASkyguardCampaignTheaterKit* FindKit(UWorld* World)
	{
		if (!World)
		{
			return nullptr;
		}
		for (TActorIterator<ASkyguardCampaignTheaterKit> It(World); It; ++It)
		{
			if (IsValid(*It))
			{
				return *It;
			}
		}
		return nullptr;
	}

	int32 CountKits(UWorld* World)
	{
		int32 Count = 0;
		if (!World)
		{
			return 0;
		}
		for (TActorIterator<ASkyguardCampaignTheaterKit> It(World); It; ++It)
		{
			if (IsValid(*It))
			{
				++Count;
			}
		}
		return Count;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardTheaterKitsAreUniquePerMissionTest,
	"Skyguard52.Campaign.TheaterKitsAreUniquePerMission",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardTheaterKitsAreUniquePerMissionTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCampaignTheaterKitTests;

	TestEqual(
		TEXT("ten theater kits match the ten-mission roster"),
		SkyguardCampaignTheaterKit::NumKits(),
		SkyguardCampaignRoster::NumMissions());
	TestTrue(
		TEXT("kit table is pairwise distinct"),
		SkyguardCampaignTheaterKit::AreKitsPairwiseDistinct());

	TSet<FName> KitIds;
	TSet<FName> Landmarks;
	TSet<FString> Fingerprints;
	for (int32 Index = 0; Index < SkyguardCampaignRoster::NumMissions(); ++Index)
	{
		const FSkyguardCampaignMissionSpec& Mission =
			SkyguardCampaignRoster::Get(Index);
		const FSkyguardTheaterKitSpec& Kit =
			SkyguardCampaignTheaterKit::Resolve(Mission.WeatherIdentity);
		const FString Label = Mission.MissionId.ToString();
		TestEqual(
			*FString::Printf(TEXT("%s kit keys off roster weather identity"), *Label),
			Kit.WeatherIdentity,
			Mission.WeatherIdentity);
		TestFalse(
			*FString::Printf(TEXT("%s has a kit id"), *Label),
			Kit.KitId.IsNone());
		TestFalse(
			*FString::Printf(TEXT("%s has a named landmark"), *Label),
			Kit.NamedLandmark.IsNone());
		TestFalse(
			*FString::Printf(TEXT("%s kit id is unique"), *Label),
			KitIds.Contains(Kit.KitId));
		TestFalse(
			*FString::Printf(TEXT("%s named landmark is unique"), *Label),
			Landmarks.Contains(Kit.NamedLandmark));
		const FString Fingerprint = SkyguardCampaignTheaterKit::Fingerprint(Kit);
		TestFalse(
			*FString::Printf(TEXT("%s fingerprint is unique"), *Label),
			Fingerprints.Contains(Fingerprint));
		TestFalse(
			*FString::Printf(TEXT("%s kit copy bans Igla/Yak/rifle"), *Label),
			CopyHasBannedTerm(Fingerprint));
		KitIds.Add(Kit.KitId);
		Landmarks.Add(Kit.NamedLandmark);
		Fingerprints.Add(Fingerprint);
	}

	for (int32 Left = 0; Left < SkyguardCampaignRoster::NumMissions(); ++Left)
	{
		const FSkyguardTheaterKitSpec& A = SkyguardCampaignTheaterKit::Resolve(
			SkyguardCampaignRoster::Get(Left).WeatherIdentity);
		for (int32 Right = Left + 1; Right < SkyguardCampaignRoster::NumMissions(); ++Right)
		{
			const FSkyguardTheaterKitSpec& B = SkyguardCampaignTheaterKit::Resolve(
				SkyguardCampaignRoster::Get(Right).WeatherIdentity);
			TestTrue(
				*FString::Printf(
					TEXT("%s and %s cannot apply the same kit"),
					*SkyguardCampaignRoster::IdAt(Left).ToString(),
					*SkyguardCampaignRoster::IdAt(Right).ToString()),
				A.KitId != B.KitId);
			TestTrue(
				*FString::Printf(
					TEXT("%s and %s swap the named landmark"),
					*SkyguardCampaignRoster::IdAt(Left).ToString(),
					*SkyguardCampaignRoster::IdAt(Right).ToString()),
				A.NamedLandmark != B.NamedLandmark);
		}
	}

	TestEqual(TEXT("ten distinct kit ids"), KitIds.Num(), 10);
	TestEqual(TEXT("ten distinct named landmarks"), Landmarks.Num(), 10);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardTheaterKitNamedLandmarkSwapsTest,
	"Skyguard52.Campaign.TheaterKitNamedLandmarkSwaps",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardTheaterKitNamedLandmarkSwapsTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardTheaterLandmarkWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardCampaignTheaterKit* Kit =
		World->SpawnActor<ASkyguardCampaignTheaterKit>();
	TestNotNull(TEXT("theater kit"), Kit);
	if (!Kit)
	{
		World->DestroyWorld(false);
		return false;
	}

	Kit->ApplyTheaterKit(TEXT("ClearNoon"));
	const FName FirstLandmark = Kit->GetNamedLandmark();
	const FName FirstKitId = Kit->GetAppliedKitId();
	const FLinearColor FirstTint = Kit->GetBuildingTint();
	TestEqual(
		TEXT("clear noon identity"),
		Kit->GetAppliedWeatherIdentity(),
		FName(TEXT("ClearNoon")));
	TestFalse(TEXT("clear noon names a landmark"), FirstLandmark.IsNone());

	Kit->ApplyTheaterKit(TEXT("HarborOvercast"));
	TestEqual(
		TEXT("harbor identity"),
		Kit->GetAppliedWeatherIdentity(),
		FName(TEXT("HarborOvercast")));
	TestTrue(
		TEXT("harbor swaps the named landmark"),
		Kit->GetNamedLandmark() != FirstLandmark);
	TestTrue(
		TEXT("harbor applies a different kit"),
		Kit->GetAppliedKitId() != FirstKitId);
	TestTrue(
		TEXT("harbor restyles building tint"),
		!Kit->GetBuildingTint().Equals(FirstTint, 0.01f));
	TestTrue(
		TEXT("harbor restyles road instances in place"),
		Kit->GetRoadInstanceCount() > 0);
	TestTrue(
		TEXT("harbor restyles building instances in place"),
		Kit->GetBuildingInstanceCount() > 0);
	TestTrue(
		TEXT("harbor restyles lamp posts in place"),
		Kit->GetLampInstanceCount() > 0);
	TestTrue(
		TEXT("harbor restyles silhouette instances in place"),
		Kit->GetSilhouetteInstanceCount() > 0);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSortieDirectorAppliesTheaterKitTest,
	"Skyguard52.Campaign.SortieAppliesTheaterKit",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortieDirectorAppliesTheaterKitTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCampaignTheaterKitTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardTheaterSortieWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("director"), Director);
	if (!Director)
	{
		World->DestroyWorld(false);
		return false;
	}

	Director->bAutoStart = false;
	Director->StartMissionIndex(0);
	ASkyguardCampaignTheaterKit* Kit = FindKit(World);
	TestNotNull(TEXT("sortie start spawns or finds a theater kit"), Kit);
	if (!Kit)
	{
		World->DestroyWorld(false);
		return false;
	}
	TestEqual(
		TEXT("M01 applies ClearNoon kit"),
		Kit->GetAppliedWeatherIdentity(),
		FName(TEXT("ClearNoon")));
	const FName FirstKitId = Kit->GetAppliedKitId();
	const FName FirstLandmark = Kit->GetNamedLandmark();

	Director->StartMissionIndex(1);
	Kit = FindKit(World);
	TestNotNull(TEXT("harbor still has one theater kit"), Kit);
	if (!Kit)
	{
		World->DestroyWorld(false);
		return false;
	}
	TestEqual(
		TEXT("M02 applies HarborOvercast kit"),
		Kit->GetAppliedWeatherIdentity(),
		FName(TEXT("HarborOvercast")));
	TestTrue(
		TEXT("two missions cannot apply the same kit"),
		Kit->GetAppliedKitId() != FirstKitId);
	TestTrue(
		TEXT("harbor swaps the named landmark on the same map"),
		Kit->GetNamedLandmark() != FirstLandmark);
	TestEqual(TEXT("still one playable-map kit actor"), CountKits(World), 1);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardTheaterKitKeepsHarborBreakerClockTest,
	"Skyguard52.Campaign.TheaterKitKeepsHarborBreakerClock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardTheaterKitKeepsHarborBreakerClockTest::RunTest(const FString& Parameters)
{
	const FSkyguardCampaignMissionSpec& Harbor = SkyguardCampaignRoster::Get(1);
	TestEqual(TEXT("harbor id"), Harbor.MissionId, FName(TEXT("M02_HarborShield")));
	const float ExpectedBeats[7] = {120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f};
	for (int32 Index = 0; Index < 7; ++Index)
	{
		TestTrue(
			*FString::Printf(TEXT("harbor beat %d stays on the 15-minute proof"), Index),
			FMath::IsNearlyEqual(Harbor.BeatSeconds[Index], ExpectedBeats[Index], 2.f));
	}
	TestEqual(
		TEXT("harbor kit still keys HarborOvercast"),
		SkyguardCampaignTheaterKit::Resolve(Harbor.WeatherIdentity).WeatherIdentity,
		FName(TEXT("HarborOvercast")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardTheaterKitCopyBansYakIglaRifleTest,
	"Skyguard52.Campaign.TheaterKitCopyBansYakIglaRifle",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardTheaterKitCopyBansYakIglaRifleTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCampaignTheaterKitTests;

	for (int32 Index = 0; Index < SkyguardCampaignTheaterKit::NumKits(); ++Index)
	{
		const FSkyguardTheaterKitSpec& Kit =
			SkyguardCampaignTheaterKit::GetByIndex(Index);
		const FString Fields[] = {
			Kit.WeatherIdentity.ToString(),
			Kit.KitId.ToString(),
			Kit.LandmarkSet.ToString(),
			Kit.BuildingKit.ToString(),
			Kit.LampTreatment.ToString(),
			Kit.RoadTreatment.ToString(),
			Kit.NamedLandmark.ToString(),
			Kit.SilhouetteKit.ToString(),
			SkyguardCampaignTheaterKit::Fingerprint(Kit)
		};
		for (const FString& Field : Fields)
		{
			TestFalse(
				*FString::Printf(TEXT("%s bans Igla/Yak/rifle"), *Field),
				CopyHasBannedTerm(Field));
		}
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardTheaterKitEveryWeatherIdentityHitsApplyToWorldTest,
	"Skyguard52.Campaign.TheaterKitEveryWeatherIdentityHitsApplyToWorld",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardTheaterKitEveryWeatherIdentityHitsApplyToWorldTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardCampaignTheaterKitTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardTheaterEveryIdentityWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	const int32 MissionCount = SkyguardCampaignRoster::NumMissions();
	TestEqual(TEXT("ten roster weather identities"), MissionCount, 10);
	TestEqual(
		TEXT("ten theater kits"),
		SkyguardCampaignTheaterKit::NumKits(),
		MissionCount);

	TSet<FName> AppliedIdentities;
	for (int32 Index = 0; Index < MissionCount; ++Index)
	{
		const FSkyguardCampaignMissionSpec& Mission =
			SkyguardCampaignRoster::Get(Index);
		const FString Label = Mission.MissionId.ToString();
		const FSkyguardTheaterKitSpec& Resolved =
			SkyguardCampaignTheaterKit::Resolve(Mission.WeatherIdentity);
		TestFalse(
			*FString::Printf(TEXT("%s roster weather identity is set"), *Label),
			Mission.WeatherIdentity.IsNone());
		TestEqual(
			*FString::Printf(
				TEXT("%s resolves to its own weather identity"),
				*Label),
			Resolved.WeatherIdentity,
			Mission.WeatherIdentity);
		TestFalse(
			*FString::Printf(TEXT("%s resolve yields a kit id"), *Label),
			Resolved.KitId.IsNone());

		ASkyguardCampaignTheaterKit::ApplyTheaterKitToWorld(
			World,
			Mission.WeatherIdentity);
		ASkyguardCampaignTheaterKit* Kit = FindKit(World);
		TestNotNull(
			*FString::Printf(
				TEXT("%s ApplyTheaterKitToWorld finds or spawns a kit"),
				*Label),
			Kit);
		if (!Kit)
		{
			World->DestroyWorld(false);
			return false;
		}

		TestEqual(
			*FString::Printf(
				TEXT("%s ApplyTheaterKitToWorld applies %s"),
				*Label,
				*Mission.WeatherIdentity.ToString()),
			Kit->GetAppliedWeatherIdentity(),
			Mission.WeatherIdentity);
		TestEqual(
			*FString::Printf(
				TEXT("%s applied kit id matches resolve"),
				*Label),
			Kit->GetAppliedKitId(),
			Resolved.KitId);
		TestEqual(
			*FString::Printf(
				TEXT("%s applied landmark matches resolve"),
				*Label),
			Kit->GetNamedLandmark(),
			Resolved.NamedLandmark);
		TestTrue(
			*FString::Printf(TEXT("%s restyles roads in place"), *Label),
			Kit->GetRoadInstanceCount() > 0);
		TestTrue(
			*FString::Printf(TEXT("%s restyles buildings in place"), *Label),
			Kit->GetBuildingInstanceCount() > 0);
		TestTrue(
			*FString::Printf(TEXT("%s restyles lamps in place"), *Label),
			Kit->GetLampInstanceCount() > 0);
		TestTrue(
			*FString::Printf(TEXT("%s restyles silhouettes in place"), *Label),
			Kit->GetSilhouetteInstanceCount() > 0);
		AppliedIdentities.Add(Kit->GetAppliedWeatherIdentity());
	}

	TestEqual(
		TEXT("every roster weather identity was applied"),
		AppliedIdentities.Num(),
		MissionCount);
	TestEqual(
		TEXT("ApplyTheaterKitToWorld keeps one playable-map kit actor"),
		CountKits(World),
		1);

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("director"), Director);
	if (!Director)
	{
		World->DestroyWorld(false);
		return false;
	}
	Director->bAutoStart = false;
	for (int32 Index = 0; Index < MissionCount; ++Index)
	{
		const FSkyguardCampaignMissionSpec& Mission =
			SkyguardCampaignRoster::Get(Index);
		Director->StartMissionIndex(Index);
		ASkyguardCampaignTheaterKit* Kit = FindKit(World);
		TestNotNull(
			*FString::Printf(
				TEXT("%s director path still has a theater kit"),
				*Mission.MissionId.ToString()),
			Kit);
		if (!Kit)
		{
			World->DestroyWorld(false);
			return false;
		}
		TestEqual(
			*FString::Printf(
				TEXT("%s StartMissionIndex reaches ApplyTheaterKitToWorld for %s"),
				*Mission.MissionId.ToString(),
				*Mission.WeatherIdentity.ToString()),
			Kit->GetAppliedWeatherIdentity(),
			Mission.WeatherIdentity);
		TestEqual(
			*FString::Printf(
				TEXT("%s director weather identity matches roster"),
				*Mission.MissionId.ToString()),
			Director->GetMissionWeatherIdentity(),
			Mission.WeatherIdentity);
	}
	TestEqual(
		TEXT("director path still one playable-map kit actor"),
		CountKits(World),
		1);

	World->DestroyWorld(false);
	return true;
}

#endif
