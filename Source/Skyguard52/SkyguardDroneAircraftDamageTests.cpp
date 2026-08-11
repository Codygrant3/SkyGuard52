#include "Misc/AutomationTest.h"

#include "SkyguardDrone.h"
#include "SkyguardGunner.h"
#include "SkyguardYak52Aircraft.h"
#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/World.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardDroneAircraftDamageWiringTest,
	"Skyguard52.Combat.Drone.AircraftDamageWiring",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDroneAircraftDamageWiringTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardDroneAircraftDamageWorld"));
	TestNotNull(TEXT("Automation world is created"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardYak52Aircraft* Aircraft = World->SpawnActor<ASkyguardYak52Aircraft>(
		ASkyguardYak52Aircraft::StaticClass(),
		FVector::ZeroVector,
		FRotator::ZeroRotator);
	ASkyguardDrone* Drone = World->SpawnActor<ASkyguardDrone>(
		ASkyguardDrone::StaticClass(),
		FVector(150.f, 0.f, 70.f),
		FRotator::ZeroRotator);
	TestNotNull(TEXT("Yak spawns"), Aircraft);
	TestNotNull(TEXT("Drone spawns"), Drone);
	if (!Aircraft || !Drone)
	{
		World->DestroyWorld(false);
		return false;
	}

	TestNotNull(TEXT("Yak hull collider exists"), Aircraft->HullCollider);
	if (Aircraft->HullCollider)
	{
		TestTrue(
			TEXT("Hull collider blocks WorldDynamic for drone sweeps"),
			Aircraft->HullCollider->GetCollisionResponseToChannel(ECC_WorldDynamic) ==
				ECR_Block);
	}

	TestTrue(
		TEXT("Undamaged Yak starts at zero damage fraction"),
		FMath::IsNearlyZero(Aircraft->GetDamageFraction()));

	Drone->ImpactAircraft(Aircraft);
	TestTrue(
		TEXT("Collision damage raises Yak damage fraction"),
		Aircraft->GetDamageFraction() > KINDA_SMALL_NUMBER);
	TestTrue(
		TEXT("ImpactAircraft destroys the drone"),
		Drone->IsDestroyed());

	// Fresh pair for explosion splash (no prior collision on this Yak).
	ASkyguardYak52Aircraft* SplashYak = World->SpawnActor<ASkyguardYak52Aircraft>(
		ASkyguardYak52Aircraft::StaticClass(),
		FVector(0.f, 2000.f, 0.f),
		FRotator::ZeroRotator);
	ASkyguardDrone* SplashDrone = World->SpawnActor<ASkyguardDrone>(
		ASkyguardDrone::StaticClass(),
		FVector(0.f, 2000.f, 0.f),
		FRotator::ZeroRotator);
	TestNotNull(TEXT("Splash Yak spawns"), SplashYak);
	TestNotNull(TEXT("Splash drone spawns"), SplashDrone);
	if (SplashYak && SplashDrone)
	{
		const float Before = SplashYak->GetDamageFraction();
		SplashDrone->ApplyBallisticHit(
			SplashDrone->MaxHealth + 1.f,
			SplashDrone->GetActorLocation(),
			FVector::ForwardVector);
		TestTrue(
			TEXT("Breakup splash damages a nearby Yak"),
			SplashYak->GetDamageFraction() > Before);
	}

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGunnerSortieAircraftDamageFromYakTest,
	"Skyguard52.Combat.Gunner.SortieAircraftDamageFromYak",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGunnerSortieAircraftDamageFromYakTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardGunnerSortieDamageWorld"));
	TestNotNull(TEXT("Automation world is created"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardYak52Aircraft* Aircraft = World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	TestNotNull(TEXT("Yak spawns"), Aircraft);
	TestNotNull(TEXT("Gunner spawns"), Gunner);
	if (!Aircraft || !Gunner || !Aircraft->GetRearGunnerMount())
	{
		World->DestroyWorld(false);
		return false;
	}

	Gunner->AttachToComponent(
		Aircraft->GetRearGunnerMount(),
		FAttachmentTransformRules::SnapToTargetNotIncludingScale);
	TestTrue(
		TEXT("Attached gunner reports zero damage before hits"),
		FMath::IsNearlyZero(Gunner->GetSortieAircraftDamageFraction()));

	Aircraft->ApplyDamage(Aircraft->MaxIntegrity * 0.25f);
	TestTrue(
		TEXT("Attached gunner reads Yak damage fraction"),
		FMath::IsNearlyEqual(
			Gunner->GetSortieAircraftDamageFraction(),
			0.25f,
			0.01f));

	World->DestroyWorld(false);
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
