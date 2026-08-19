#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardArcadeLookComponent.h"
#include "SkyguardCampaignRoster.h"
#include "SkyguardCoastalEnvironmentDirector.h"
#include "SkyguardMissionTypes.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Misc/AutomationTest.h"

/**
 * Coastal director weather identity — not the theater kit.
 * Drives every ESkyguardMissionWeather through ApplyMissionWeather
 * and asserts identity / wind mood / arcade fog visibility already
 * exposed on that path. Does not invent weather types or retune wind.
 */
namespace SkyguardCoastalWeatherIdentityTests
{
	TArray<ESkyguardMissionWeather> AllMissionWeathers()
	{
		TArray<ESkyguardMissionWeather> Values;
		const UEnum* Enum = StaticEnum<ESkyguardMissionWeather>();
		if (!Enum)
		{
			return Values;
		}
		// UENUM appends _MAX as the last entry. Walk the real enumerators.
		const int32 Count = FMath::Max(0, Enum->NumEnums() - 1);
		for (int32 Index = 0; Index < Count; ++Index)
		{
			const int64 Raw = Enum->GetValueByIndex(Index);
			if (Raw == INDEX_NONE)
			{
				continue;
			}
			Values.Add(static_cast<ESkyguardMissionWeather>(Raw));
		}
		return Values;
	}

	FString EnumName(const ESkyguardMissionWeather Weather)
	{
		const UEnum* Enum = StaticEnum<ESkyguardMissionWeather>();
		return Enum
			? Enum->GetNameStringByValue(static_cast<int64>(Weather))
			: FString(TEXT("Unknown"));
	}

	int32 WindSignature(const ASkyguardCoastalEnvironmentDirector* Coast)
	{
		if (!Coast)
		{
			return 0;
		}
		return FMath::RoundToInt(Coast->WindStrength * 100.f) * 1000 +
			FMath::RoundToInt(Coast->WindSpeed * 100.f);
	}

	int32 CountMoodActors(UWorld* World)
	{
		int32 Count = 0;
		if (!World)
		{
			return 0;
		}
		for (TActorIterator<AActor> It(World); It; ++It)
		{
			if (IsValid(*It) && It->ActorHasTag(TEXT("Skyguard.ArcadeMood")))
			{
				++Count;
			}
		}
		return Count;
	}

	float MoodFogDensity(UWorld* World)
	{
		if (!World)
		{
			return -1.f;
		}
		for (TActorIterator<AExponentialHeightFog> It(World); It; ++It)
		{
			if (!IsValid(*It) || !It->ActorHasTag(TEXT("Skyguard.ArcadeMood")))
			{
				continue;
			}
			if (UExponentialHeightFogComponent* Fog = It->GetComponent())
			{
				return Fog->FogDensity;
			}
		}
		return -1.f;
	}

	int32 FogSignature(const float Density)
	{
		return FMath::RoundToInt(Density * 1000.f);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCoastalEveryMissionWeatherHitsApplyTest,
	"Skyguard52.Environment.CoastalEveryMissionWeatherHitsApply",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCoastalEveryMissionWeatherHitsApplyTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardCoastalWeatherIdentityTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardCoastalWeatherIdentityWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardCoastalEnvironmentDirector* Coast =
		World->SpawnActor<ASkyguardCoastalEnvironmentDirector>();
	TestNotNull(TEXT("coastal weather director"), Coast);
	if (!Coast)
	{
		World->DestroyWorld(false);
		return false;
	}
	TestTrue(TEXT("coastal wind source exists"), IsValid(Coast->WindSource));

	const TArray<ESkyguardMissionWeather> Weathers = AllMissionWeathers();
	static const ESkyguardMissionWeather ExpectedWeathers[] = {
		ESkyguardMissionWeather::Clear,
		ESkyguardMissionWeather::Overcast,
		ESkyguardMissionWeather::Rain,
		ESkyguardMissionWeather::Storm,
		ESkyguardMissionWeather::NightClear,
		ESkyguardMissionWeather::NightOvercast
	};
	TestEqual(
		TEXT("six ESkyguardMissionWeather enumerators on main"),
		Weathers.Num(),
		UE_ARRAY_COUNT(ExpectedWeathers));
	for (const ESkyguardMissionWeather Expected : ExpectedWeathers)
	{
		TestTrue(
			*FString::Printf(
				TEXT("%s is a reflected mission weather"),
				*EnumName(Expected)),
			Weathers.Contains(Expected));
	}

	TSet<int32> WindSignatures;
	TSet<int32> FogSignatures;
	float StormWind = -1.f;
	float RainWind = -1.f;
	float OvercastWind = -1.f;
	float ClearWind = -1.f;
	float NightClearWind = -1.f;
	float NightOvercastWind = -1.f;
	float ClearFog = -1.f;
	float StormFog = -1.f;

	for (const ESkyguardMissionWeather Weather : Weathers)
	{
		const FString Label(EnumName(Weather));
		Coast->ApplyMissionWeather(Weather);
		TestEqual(
			*FString::Printf(
				TEXT("%s ApplyMissionWeather sticks as coastal identity"),
				*Label),
			Coast->GetAppliedWeather(),
			Weather);
		TestTrue(
			*FString::Printf(TEXT("%s weather label is set"), *Label),
			FCString::Strlen(SkyguardCampaignRoster::WeatherEnumLabel(Weather)) > 0);
		TestTrue(
			*FString::Printf(TEXT("%s weather label is not Unknown"), *Label),
			FString(SkyguardCampaignRoster::WeatherEnumLabel(Weather)) !=
				TEXT("Unknown"));
		TestTrue(
			*FString::Printf(TEXT("%s coastal wind strength is in range"), *Label),
			Coast->WindStrength > 0.f && Coast->WindStrength <= 1.f);
		TestTrue(
			*FString::Printf(TEXT("%s coastal wind speed is in range"), *Label),
			Coast->WindSpeed > 0.f && Coast->WindSpeed <= 1.f);

		const bool bAddedWind = !WindSignatures.Contains(WindSignature(Coast));
		WindSignatures.Add(WindSignature(Coast));
		TestTrue(
			*FString::Printf(
				TEXT("%s coastal wind mood is distinct from the other weathers"),
				*Label),
			bAddedWind);

		USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(World, Weather, 12.f);
		TestTrue(
			*FString::Printf(TEXT("%s arcade mood identity is applied"), *Label),
			CountMoodActors(World) >= 1);
		const float Density = MoodFogDensity(World);
		TestTrue(
			*FString::Printf(TEXT("%s mood fog visibility is applied"), *Label),
			Density > 0.f);
		const bool bAddedFog = !FogSignatures.Contains(FogSignature(Density));
		FogSignatures.Add(FogSignature(Density));
		TestTrue(
			*FString::Printf(
				TEXT("%s mood fog visibility is distinct from the other weathers"),
				*Label),
			bAddedFog);

		switch (Weather)
		{
		case ESkyguardMissionWeather::Storm:
			StormWind = Coast->WindStrength;
			StormFog = Density;
			break;
		case ESkyguardMissionWeather::Rain:
			RainWind = Coast->WindStrength;
			break;
		case ESkyguardMissionWeather::Overcast:
			OvercastWind = Coast->WindStrength;
			break;
		case ESkyguardMissionWeather::Clear:
			ClearWind = Coast->WindStrength;
			ClearFog = Density;
			break;
		case ESkyguardMissionWeather::NightClear:
			NightClearWind = Coast->WindStrength;
			break;
		case ESkyguardMissionWeather::NightOvercast:
			NightOvercastWind = Coast->WindStrength;
			break;
		}
	}

	TestEqual(
		TEXT("every mission weather produced a unique coastal wind mood"),
		WindSignatures.Num(),
		Weathers.Num());
	TestEqual(
		TEXT("every mission weather produced a unique mood fog visibility"),
		FogSignatures.Num(),
		Weathers.Num());
	TestTrue(TEXT("storm wind is hard"), StormWind >= 0.85f);
	TestTrue(TEXT("storm wind is harder than rain"), StormWind > RainWind);
	TestTrue(TEXT("rain wind is harder than overcast"), RainWind > OvercastWind);
	TestTrue(TEXT("overcast wind is harder than clear"), OvercastWind > ClearWind);
	TestTrue(
		TEXT("night clear is the calmest coastal wind"),
		NightClearWind > 0.f && NightClearWind < ClearWind);
	TestTrue(
		TEXT("night overcast wind sits between night clear and overcast"),
		NightOvercastWind > NightClearWind && NightOvercastWind < OvercastWind);
	TestTrue(
		TEXT("storm fog is thicker than clear"),
		StormFog > ClearFog);

	World->DestroyWorld(false);
	return true;
}

#endif
