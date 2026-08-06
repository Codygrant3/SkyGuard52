#include "Misc/AutomationTest.h"

#include "SkyguardDrone.h"
#include "SkyguardIglaMissile.h"
#include "Engine/World.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardIglaMissileLaunchContractTest,
	"Skyguard52.Combat.Igla.GuidanceAndArming",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardIglaMissileLaunchContractTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(EWorldType::Game, false, TEXT("SkyguardIglaAutomationWorld"));
	TestNotNull(TEXT("Automation world is created"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardDrone* Target = World->SpawnActor<ASkyguardDrone>(
		ASkyguardDrone::StaticClass(),
		FVector(4000.f, 0.f, 0.f),
		FRotator::ZeroRotator);
	ASkyguardIglaMissile* Missile = World->SpawnActor<ASkyguardIglaMissile>(
		ASkyguardIglaMissile::StaticClass(),
		FVector::ZeroVector,
		FRotator::ZeroRotator);
	TestNotNull(TEXT("Igla target spawns"), Target);
	TestNotNull(TEXT("Igla missile spawns"), Missile);

	if (Missile && Target)
	{
		Missile->InitializeMissile(Target, 160.f, FVector::ForwardVector);
		TestTrue(
			TEXT("Missile retains its designated target"),
			Missile->GetTargetActor() == static_cast<AActor*>(Target));
		TestFalse(TEXT("Missile is not armed at launch"), Missile->IsArmed());
		Missile->Tick(0.2f);
		TestTrue(TEXT("Missile arms only after its launch delay"), Missile->IsArmed());
		TestTrue(TEXT("Missile travels out of the launcher front"), Missile->GetActorLocation().X > 0.f);
	}

	World->DestroyWorld(false);
	return true;
}

#endif
