#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardArcadeLookComponent.h"
#include "Camera/CameraComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Misc/AutomationTest.h"

namespace SkyguardArcadeLookTests
{
	int32 CountMoodActors(UWorld* World)
	{
		int32 Count = 0;
		if (!World)
		{
			return Count;
		}
		for (TActorIterator<AActor> It(World); It; ++It)
		{
			if (It->ActorHasTag(TEXT("Skyguard.ArcadeMood")))
			{
				++Count;
			}
		}
		return Count;
	}

	APostProcessVolume* FindMoodVolume(UWorld* World)
	{
		if (!World)
		{
			return nullptr;
		}
		for (TActorIterator<APostProcessVolume> It(World); It; ++It)
		{
			if (It->ActorHasTag(TEXT("Skyguard.ArcadeMood")))
			{
				return *It;
			}
		}
		return nullptr;
	}

	UExponentialHeightFogComponent* FindMoodFog(UWorld* World)
	{
		if (!World)
		{
			return nullptr;
		}
		for (TActorIterator<AExponentialHeightFog> It(World); It; ++It)
		{
			if (!It->ActorHasTag(TEXT("Skyguard.ArcadeMood")))
			{
				continue;
			}
			if (UExponentialHeightFogComponent* Fog = It->GetComponent())
			{
				return Fog;
			}
		}
		return nullptr;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardArcadeLookAppliesCombatGradeTest,
	"Skyguard52.Arcade.LookAppliesDuskCombatGrade",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardArcadeLookAppliesCombatGradeTest::RunTest(const FString& Parameters)
{
	USkyguardArcadeLookComponent* Look = NewObject<USkyguardArcadeLookComponent>();
	UCameraComponent* Camera = NewObject<UCameraComponent>();
	TestNotNull(TEXT("look"), Look);
	TestNotNull(TEXT("camera"), Camera);
	if (!Look || !Camera)
	{
		return false;
	}

	TestTrue(TEXT("enabled by default"), Look->IsEnabled());
	TestTrue(TEXT("contrast above identity"), Look->Contrast > 1.f);
	Look->ApplyToCamera(Camera);
	TestEqual(TEXT("blend weight"), Camera->PostProcessBlendWeight, 1.f);
	TestTrue(TEXT("bloom override"), Camera->PostProcessSettings.bOverride_BloomIntensity);
	Look->ApplyTargetingSensor(Camera);
	TestTrue(
		TEXT("sensor is more saturated in the green channel than red"),
		Camera->PostProcessSettings.ColorGain.Y >
			Camera->PostProcessSettings.ColorGain.X);
	TestTrue(
		TEXT("sensor vignette is heavier than helmet"),
		Camera->PostProcessSettings.VignetteIntensity > 0.6f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardArcadeWorldMoodIsIdempotentTest,
	"Skyguard52.Arcade.WorldMoodSpawnsOnce",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardArcadeWorldMoodIsIdempotentTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardArcadeMoodWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	USkyguardArcadeLookComponent::ApplyWorldMood(World);
	USkyguardArcadeLookComponent::ApplyWorldMood(World);
	int32 MoodActors = 0;
	for (TActorIterator<AActor> It(World); It; ++It)
	{
		if (It->ActorHasTag(TEXT("Skyguard.ArcadeMood")))
		{
			++MoodActors;
		}
	}
	TestTrue(TEXT("mood actors spawned"), MoodActors >= 2);
	TestTrue(TEXT("second apply is a no-op"), MoodActors <= 3);
	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardArcadeLookAppliesHelmetOverlayTest,
	"Skyguard52.Arcade.LookAppliesHelmetOverlay",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardArcadeLookAppliesHelmetOverlayTest::RunTest(const FString& Parameters)
{
	USkyguardArcadeLookComponent* Look = NewObject<USkyguardArcadeLookComponent>();
	UCameraComponent* Camera = NewObject<UCameraComponent>();
	TestNotNull(TEXT("look"), Look);
	TestNotNull(TEXT("camera"), Camera);
	if (!Look || !Camera)
	{
		return false;
	}

	const FPostProcessSettings& Settings = Camera->PostProcessSettings;
	TestFalse(
		TEXT("visor fringe is not applied without the helmet API"),
		Settings.bOverride_SceneFringeIntensity);
	TestFalse(
		TEXT("helmet vignette is not applied without the helmet API"),
		Settings.bOverride_VignetteIntensity);
	TestFalse(
		TEXT("helmet gain is not applied without the helmet API"),
		Settings.bOverride_ColorGain);
	TestFalse(
		TEXT("identity gain is not a warm visor"),
		Settings.ColorGain.X > Settings.ColorGain.Z);

	Look->ApplyHelmetSight(Camera);

	TestTrue(TEXT("helmet API enables visor fringe"), Settings.bOverride_SceneFringeIntensity);
	TestTrue(TEXT("helmet API enables vignette"), Settings.bOverride_VignetteIntensity);
	TestTrue(TEXT("helmet API enables gain"), Settings.bOverride_ColorGain);
	TestTrue(TEXT("visor fringe is above identity"), Settings.SceneFringeIntensity > 0.f);
	TestTrue(TEXT("helmet vignette is applied"), Settings.VignetteIntensity > 0.f);
	TestTrue(
		TEXT("helmet visor is a warm grade, not identity"),
		Settings.ColorGain.X > Settings.ColorGain.Z);
	TestTrue(
		TEXT("helmet saturation keeps a dusk blue lift"),
		Settings.ColorSaturation.Z > Settings.ColorSaturation.X);
	TestEqual(TEXT("helmet blend weight"), Camera->PostProcessBlendWeight, 1.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardArcadeLookAppliesThermalNightLookTest,
	"Skyguard52.Arcade.LookAppliesThermalNightLook",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardArcadeLookAppliesThermalNightLookTest::RunTest(const FString& Parameters)
{
	USkyguardArcadeLookComponent* Look = NewObject<USkyguardArcadeLookComponent>();
	UCameraComponent* Camera = NewObject<UCameraComponent>();
	TestNotNull(TEXT("look"), Look);
	TestNotNull(TEXT("camera"), Camera);
	if (!Look || !Camera)
	{
		return false;
	}

	const FPostProcessSettings& Settings = Camera->PostProcessSettings;
	TestFalse(
		TEXT("thermal gain is not applied without the thermal API"),
		Settings.bOverride_ColorGain);
	TestFalse(
		TEXT("identity is not a white-hot night thermal"),
		Settings.ColorGain.X > 1.4f);
	TestFalse(
		TEXT("identity is not a desaturated night thermal"),
		Settings.ColorSaturation.X < 0.15f);

	Look->ApplyHelmetSight(Camera);
	TestFalse(
		TEXT("helmet visor is not the night thermal grade"),
		Settings.ColorGain.X > 1.4f);

	Look->ApplyThermalSensor(Camera);

	TestTrue(TEXT("thermal API enables gain"), Settings.bOverride_ColorGain);
	TestTrue(TEXT("thermal API enables saturation"), Settings.bOverride_ColorSaturation);
	TestTrue(
		TEXT("night thermal is white-hot, red over green"),
		Settings.ColorGain.X > Settings.ColorGain.Y);
	TestTrue(
		TEXT("night thermal falls off toward blue"),
		Settings.ColorGain.Y > Settings.ColorGain.Z);
	TestTrue(
		TEXT("night thermal gain is hotter than helmet"),
		Settings.ColorGain.X > 1.4f);
	TestTrue(
		TEXT("night thermal is desaturated"),
		Settings.ColorSaturation.X < 0.15f
			&& Settings.ColorSaturation.Y < 0.15f
			&& Settings.ColorSaturation.Z < 0.15f);
	TestTrue(TEXT("night thermal bloom is hotter than helmet"), Settings.BloomIntensity > 1.f);
	TestEqual(TEXT("thermal blend weight"), Camera->PostProcessBlendWeight, 1.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardArcadeLookAppliesWeatherMoodTest,
	"Skyguard52.Arcade.LookAppliesWeatherMood",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardArcadeLookAppliesWeatherMoodTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardArcadeLookTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardArcadeWeatherMoodWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	TestEqual(
		TEXT("weather mood is not spawned without the weather API"),
		CountMoodActors(World),
		0);
	TestFalse(
		TEXT("night mood volume does not exist without the weather API"),
		FindMoodVolume(World) != nullptr);

	USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(
		World,
		ESkyguardMissionWeather::NightClear,
		12.f);

	APostProcessVolume* Volume = FindMoodVolume(World);
	UExponentialHeightFogComponent* Fog = FindMoodFog(World);
	TestNotNull(TEXT("night weather API spawned a mood volume"), Volume);
	TestNotNull(TEXT("night weather API spawned mood fog"), Fog);
	if (!Volume || !Fog)
	{
		World->DestroyWorld(false);
		return false;
	}

	TestTrue(TEXT("weather mood is unbound"), Volume->bUnbound);
	TestTrue(
		TEXT("night weather exposure is darker than day identity"),
		Volume->Settings.AutoExposureBias < -1.f);
	TestTrue(
		TEXT("night weather vignette is heavier than the default overcast mood"),
		Volume->Settings.VignetteIntensity > 0.45f);
	const float NightFogDensity = Fog->FogDensity;
	TestTrue(TEXT("night weather thickens fog"), NightFogDensity > 0.03f);

	USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(
		World,
		ESkyguardMissionWeather::Clear,
		12.f);
	TestTrue(
		TEXT("clear weather lifts night exposure"),
		Volume->Settings.AutoExposureBias > -0.3f);
	TestTrue(
		TEXT("clear weather thins fog versus night"),
		Fog->FogDensity < NightFogDensity);
	TestTrue(
		TEXT("clear weather vignette is lighter than night"),
		Volume->Settings.VignetteIntensity < 0.45f);

	USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(
		World,
		ESkyguardMissionWeather::Storm,
		12.f);
	TestTrue(
		TEXT("storm weather is denser than clear"),
		Fog->FogDensity > 0.04f);
	TestTrue(
		TEXT("storm weather stays darker than clear"),
		Volume->Settings.AutoExposureBias < -0.5f);

	World->DestroyWorld(false);
	return true;
}

#endif
