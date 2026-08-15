#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardArcadeLookComponent.h"
#include "Camera/CameraComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Misc/AutomationTest.h"

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

#endif
