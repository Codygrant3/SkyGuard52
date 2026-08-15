#include "SkyguardArcadeLookComponent.h"
#include "Camera/CameraComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/Scene.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"

USkyguardArcadeLookComponent::USkyguardArcadeLookComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void USkyguardArcadeLookComponent::ApplyToCamera(UCameraComponent* Camera)
{
	ApplyHelmetSight(Camera);
}

void USkyguardArcadeLookComponent::ApplyHelmetSight(UCameraComponent* Camera)
{
	if (!bEnabled || !Camera)
	{
		return;
	}

	FPostProcessSettings& Settings = Camera->PostProcessSettings;
	Settings.bOverride_ColorContrast = true;
	Settings.ColorContrast = FVector4(Contrast, Contrast, Contrast, Contrast);
	Settings.bOverride_ColorSaturation = true;
	Settings.ColorSaturation = FVector4(Saturation, Saturation, Saturation + 0.06f, Saturation);
	Settings.bOverride_ColorGain = true;
	Settings.ColorGain = FVector4(Gain + 0.04f, Gain, Gain - 0.02f, Gain);
	Settings.bOverride_ColorGamma = true;
	Settings.ColorGamma = FVector4(Gamma, Gamma, Gamma + 0.03f, Gamma);

	Settings.bOverride_BloomIntensity = true;
	Settings.BloomIntensity = BloomIntensity;
	Settings.bOverride_BloomThreshold = true;
	Settings.BloomThreshold = 0.85f;

	Settings.bOverride_VignetteIntensity = true;
	Settings.VignetteIntensity = Vignette;

	Settings.bOverride_FilmGrainIntensity = true;
	Settings.FilmGrainIntensity = Grain;

	Settings.bOverride_SceneFringeIntensity = true;
	Settings.SceneFringeIntensity = ChromaticAberration;

	Settings.bOverride_AutoExposureBias = true;
	Settings.AutoExposureBias = 0.15f;
	Settings.bOverride_AutoExposureMinBrightness = true;
	Settings.AutoExposureMinBrightness = 0.08f;
	Settings.bOverride_AutoExposureMaxBrightness = true;
	Settings.AutoExposureMaxBrightness = 1.6f;

	Camera->PostProcessBlendWeight = 1.f;
}

void USkyguardArcadeLookComponent::ApplyTargetingSensor(UCameraComponent* Camera)
{
	if (!bEnabled || !Camera)
	{
		return;
	}

	FPostProcessSettings& Settings = Camera->PostProcessSettings;
	Settings.bOverride_ColorSaturation = true;
	Settings.ColorSaturation = FVector4(0.12f, 0.55f, 0.18f, 0.2f);
	Settings.bOverride_ColorContrast = true;
	Settings.ColorContrast = FVector4(1.45f, 1.55f, 1.35f, 1.45f);
	Settings.bOverride_ColorGain = true;
	Settings.ColorGain = FVector4(0.55f, 1.25f, 0.62f, 1.f);
	Settings.bOverride_ColorGamma = true;
	Settings.ColorGamma = FVector4(0.82f, 0.88f, 0.8f, 0.85f);
	Settings.bOverride_BloomIntensity = true;
	Settings.BloomIntensity = 1.15f;
	Settings.bOverride_VignetteIntensity = true;
	Settings.VignetteIntensity = 0.72f;
	Settings.bOverride_FilmGrainIntensity = true;
	Settings.FilmGrainIntensity = 0.22f;
	Settings.bOverride_SceneFringeIntensity = true;
	Settings.SceneFringeIntensity = 0.05f;
	Settings.bOverride_AutoExposureBias = true;
	Settings.AutoExposureBias = 0.45f;
	Camera->PostProcessBlendWeight = 1.f;
}

void USkyguardArcadeLookComponent::ApplyThermalSensor(UCameraComponent* Camera)
{
	if (!bEnabled || !Camera)
	{
		return;
	}

	FPostProcessSettings& Settings = Camera->PostProcessSettings;
	Settings.bOverride_ColorSaturation = true;
	Settings.ColorSaturation = FVector4(0.05f, 0.08f, 0.04f, 0.1f);
	Settings.bOverride_ColorContrast = true;
	Settings.ColorContrast = FVector4(1.7f, 1.35f, 1.15f, 1.5f);
	Settings.bOverride_ColorGain = true;
	Settings.ColorGain = FVector4(1.55f, 0.55f, 0.22f, 1.f);
	Settings.bOverride_ColorGamma = true;
	Settings.ColorGamma = FVector4(0.78f, 0.9f, 1.05f, 0.88f);
	Settings.bOverride_BloomIntensity = true;
	Settings.BloomIntensity = 1.6f;
	Settings.bOverride_VignetteIntensity = true;
	Settings.VignetteIntensity = 0.62f;
	Settings.bOverride_FilmGrainIntensity = true;
	Settings.FilmGrainIntensity = 0.28f;
	Settings.bOverride_AutoExposureBias = true;
	Settings.AutoExposureBias = 0.7f;
	Camera->PostProcessBlendWeight = 1.f;
}

void USkyguardArcadeLookComponent::ApplyWorldMood(UObject* WorldContextObject)
{
	ApplyWorldMoodForWeather(WorldContextObject, ESkyguardMissionWeather::Overcast);
}

void USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(
	UObject* WorldContextObject,
	const ESkyguardMissionWeather Weather)
{
	UWorld* World = WorldContextObject
		? WorldContextObject->GetWorld()
		: nullptr;
	if (!World)
	{
		return;
	}

	const FName MoodTag(TEXT("Skyguard.ArcadeMood"));
	APostProcessVolume* Volume = nullptr;
	AExponentialHeightFog* Fog = nullptr;
	for (TActorIterator<AActor> It(World); It; ++It)
	{
		if (!IsValid(*It) || !It->ActorHasTag(MoodTag))
		{
			continue;
		}
		if (!Volume)
		{
			Volume = Cast<APostProcessVolume>(*It);
		}
		if (!Fog)
		{
			Fog = Cast<AExponentialHeightFog>(*It);
		}
	}

	FActorSpawnParameters Params;
	Params.SpawnCollisionHandlingOverride =
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	if (!Volume)
	{
		Volume = World->SpawnActor<APostProcessVolume>(
			FVector::ZeroVector, FRotator::ZeroRotator, Params);
		if (Volume)
		{
			Volume->Tags.Add(MoodTag);
			Volume->bEnabled = true;
			Volume->bUnbound = true;
			Volume->BlendWeight = 1.f;
			Volume->Priority = 80.f;
		}
	}

	float Contrast = 1.22f;
	float Saturation = 1.08f;
	float Bloom = 0.7f;
	float Vignette = 0.38f;
	float Exposure = -0.35f;
	float FogDensity = 0.024f;
	FLinearColor FogColor(0.10f, 0.16f, 0.30f);
	FLinearColor SunColor(1.f, 0.62f, 0.38f);
	float SunScale = 0.35f;
	switch (Weather)
	{
	case ESkyguardMissionWeather::NightClear:
	case ESkyguardMissionWeather::NightOvercast:
		Contrast = 1.32f;
		Saturation = 0.78f;
		Bloom = 0.45f;
		Vignette = 0.52f;
		Exposure = -1.15f;
		FogDensity = 0.038f;
		FogColor = FLinearColor(0.04f, 0.06f, 0.14f);
		SunColor = FLinearColor(0.35f, 0.42f, 0.7f);
		SunScale = 0.12f;
		break;
	case ESkyguardMissionWeather::Storm:
		Contrast = 1.18f;
		Saturation = 0.72f;
		Bloom = 0.35f;
		Exposure = -0.7f;
		FogDensity = 0.048f;
		FogColor = FLinearColor(0.14f, 0.16f, 0.18f);
		SunColor = FLinearColor(0.55f, 0.58f, 0.62f);
		SunScale = 0.18f;
		break;
	case ESkyguardMissionWeather::Rain:
		Contrast = 1.2f;
		Saturation = 0.88f;
		FogDensity = 0.034f;
		FogColor = FLinearColor(0.12f, 0.16f, 0.22f);
		SunScale = 0.22f;
		break;
	case ESkyguardMissionWeather::Clear:
		Contrast = 1.16f;
		Saturation = 1.14f;
		Exposure = -0.12f;
		FogDensity = 0.014f;
		FogColor = FLinearColor(0.18f, 0.22f, 0.32f);
		SunColor = FLinearColor(1.f, 0.78f, 0.52f);
		SunScale = 0.55f;
		break;
	case ESkyguardMissionWeather::Overcast:
	default:
		break;
	}

	if (Volume)
	{
		FPostProcessSettings& Settings = Volume->Settings;
		Settings.bOverride_ColorContrast = true;
		Settings.ColorContrast = FVector4(Contrast, Contrast, Contrast, Contrast);
		Settings.bOverride_ColorSaturation = true;
		Settings.ColorSaturation = FVector4(Saturation, Saturation, Saturation + 0.04f, Saturation);
		Settings.bOverride_BloomIntensity = true;
		Settings.BloomIntensity = Bloom;
		Settings.bOverride_VignetteIntensity = true;
		Settings.VignetteIntensity = Vignette;
		Settings.bOverride_AutoExposureBias = true;
		Settings.AutoExposureBias = Exposure;
		Settings.bOverride_AutoExposureMinBrightness = true;
		Settings.AutoExposureMinBrightness = 0.03f;
		Settings.bOverride_AutoExposureMaxBrightness = true;
		Settings.AutoExposureMaxBrightness = 1.2f;
	}

	if (!Fog)
	{
		Fog = World->SpawnActor<AExponentialHeightFog>(
			FVector(0.f, 0.f, 400.f), FRotator::ZeroRotator, Params);
		if (Fog)
		{
			Fog->Tags.Add(MoodTag);
		}
	}
	if (Fog)
	{
		if (UExponentialHeightFogComponent* FogComponent = Fog->GetComponent())
		{
			FogComponent->SetFogDensity(FogDensity);
			FogComponent->SetFogHeightFalloff(0.18f);
			FogComponent->SetFogMaxOpacity(0.88f);
			FogComponent->SetFogInscatteringColor(FogColor);
			FogComponent->SetDirectionalInscatteringColor(SunColor);
			FogComponent->SetDirectionalInscatteringExponent(12.f);
			FogComponent->SetDirectionalInscatteringStartDistance(800.f);
		}
	}

	for (TActorIterator<ADirectionalLight> It(World); It; ++It)
	{
		ADirectionalLight* Sun = *It;
		if (!IsValid(Sun))
		{
			continue;
		}
		if (UDirectionalLightComponent* Light = Sun->GetComponent())
		{
			Light->SetIntensity(FMath::Clamp(6.f * SunScale / 0.35f, 0.6f, 8.f));
			Light->SetLightColor(SunColor);
		}
	}
}
