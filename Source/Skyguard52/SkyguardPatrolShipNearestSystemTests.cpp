#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGunshipTypes.h"
#include "SkyguardPatrolShipBoss.h"

#include "Components/PrimitiveComponent.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace
{
	// Known constructor offsets on ASkyguardPatrolShipBoss parts.
	const FVector RadarOffset(-280.f, 0.f, 620.f);
	const FVector CannonOffset(620.f, 0.f, 340.f);
	const FVector LauncherOffset(220.f, 0.f, 320.f);

	void KillSystem(ASkyguardPatrolShipBoss* Ship, const ESkyguardPatrolShipSystem System)
	{
		Ship->ApplyHitToSystem(System, 500.f);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPatrolShipFindNearestLiveSystemTest,
	"Skyguard52.Campaign.PatrolShipFindNearestLiveSystem",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPatrolShipFindNearestLiveSystemTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardShipNearestWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardPatrolShipBoss* Ship = World->SpawnActor<ASkyguardPatrolShipBoss>(
		FVector::ZeroVector,
		FRotator::ZeroRotator);
	TestNotNull(TEXT("ship"), Ship);
	if (!Ship)
	{
		World->DestroyWorld(false);
		return false;
	}

	UPrimitiveComponent* Radar = Ship->GetSystemComponent(
		ESkyguardPatrolShipSystem::Radar);
	UPrimitiveComponent* Cannon = Ship->GetSystemComponent(
		ESkyguardPatrolShipSystem::Cannon);
	UPrimitiveComponent* Launcher = Ship->GetSystemComponent(
		ESkyguardPatrolShipSystem::Launcher);
	TestNotNull(TEXT("radar mesh"), Radar);
	TestNotNull(TEXT("CIWS / cannon mesh"), Cannon);
	TestNotNull(TEXT("launcher mesh"), Launcher);
	if (!Radar || !Cannon || !Launcher)
	{
		World->DestroyWorld(false);
		return false;
	}

	TestTrue(
		TEXT("radar relative offset is -280/620"),
		Radar->GetRelativeLocation().Equals(RadarOffset));
	TestTrue(
		TEXT("CIWS / cannon relative offset is +620/340"),
		Cannon->GetRelativeLocation().Equals(CannonOffset));
	TestTrue(
		TEXT("launcher relative offset is +220/320"),
		Launcher->GetRelativeLocation().Equals(LauncherOffset));

	const FVector Origin = Ship->GetActorLocation();
	const FVector RadarWorld = Origin + RadarOffset;
	const FVector CannonWorld = Origin + CannonOffset;
	const FVector LauncherWorld = Origin + LauncherOffset;

	TestTrue(
		TEXT("radar world location is origin plus -280/620"),
		Radar->GetComponentLocation().Equals(RadarWorld, 1.f));
	TestTrue(
		TEXT("cannon world location is origin plus +620/340"),
		Cannon->GetComponentLocation().Equals(CannonWorld, 1.f));
	TestTrue(
		TEXT("launcher world location is origin plus +220/320"),
		Launcher->GetComponentLocation().Equals(LauncherWorld, 1.f));

	TestTrue(
		TEXT("nearest to radar offset is the live radar mesh"),
		Ship->FindNearestLiveSystem(RadarWorld) == Radar);
	TestTrue(
		TEXT("nearest to CIWS / cannon offset is the live cannon mesh"),
		Ship->FindNearestLiveSystem(CannonWorld) == Cannon);
	TestTrue(
		TEXT("nearest to launcher offset is the live launcher mesh"),
		Ship->FindNearestLiveSystem(LauncherWorld) == Launcher);

	// Between launcher (+220/320) and CIWS (+620/340), still closer to launcher.
	const FVector BetweenLauncherAndCannon = Origin + FVector(350.f, 0.f, 325.f);
	TestTrue(
		TEXT("nearest to a point closer to +220/320 than +620/340 is launcher"),
		Ship->FindNearestLiveSystem(BetweenLauncherAndCannon) == Launcher);

	KillSystem(Ship, ESkyguardPatrolShipSystem::Radar);
	TestTrue(TEXT("radar is dead"), Ship->IsRadarDead());
	UPrimitiveComponent* AfterRadar = Ship->FindNearestLiveSystem(RadarWorld);
	UPrimitiveComponent* Deck = Ship->GetSystemComponent(
		ESkyguardPatrolShipSystem::DroneDeck);
	TestNotNull(TEXT("nearest after radar kill still finds a live mesh"), AfterRadar);
	TestNotNull(TEXT("drone deck mesh"), Deck);
	TestTrue(
		TEXT("nearest at the dead radar offset skips the dead radar mesh"),
		AfterRadar != Radar);
	// From -280/620 the remaining live parts are deck (80/370), launcher
	// (+220/320), engines (-820/200), then CIWS (+620/340). Deck is closest.
	TestTrue(
		TEXT("nearest at dead radar (-280/620) is the closer live deck mesh"),
		AfterRadar == Deck);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPatrolShipPriorityAfterTwoKillsTest,
	"Skyguard52.Campaign.PatrolShipPriorityAfterTwoKills",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPatrolShipPriorityAfterTwoKillsTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardShipPriorityWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardPatrolShipBoss* Ship = World->SpawnActor<ASkyguardPatrolShipBoss>(
		FVector::ZeroVector,
		FRotator::ZeroRotator);
	TestNotNull(TEXT("ship"), Ship);
	if (!Ship)
	{
		World->DestroyWorld(false);
		return false;
	}

	TestTrue(
		TEXT("priority starts at radar"),
		Ship->GetPriorityLiveSystem() == ESkyguardPatrolShipSystem::Radar);

	KillSystem(Ship, ESkyguardPatrolShipSystem::Radar);
	TestTrue(
		TEXT("after radar, priority is cannon"),
		Ship->GetPriorityLiveSystem() == ESkyguardPatrolShipSystem::Cannon);

	KillSystem(Ship, ESkyguardPatrolShipSystem::Cannon);
	TestEqual(TEXT("two systems destroyed"), Ship->GetDestroyedSystemCount(), 2);
	TestTrue(
		TEXT("after Radar then Cannon, priority live system is Launcher (LNCH)"),
		Ship->GetPriorityLiveSystem() == ESkyguardPatrolShipSystem::Launcher);

	KillSystem(Ship, ESkyguardPatrolShipSystem::Launcher);
	TestEqual(TEXT("three systems destroyed"), Ship->GetDestroyedSystemCount(), 3);
	TestTrue(
		TEXT("after three kills, priority live system is Engines"),
		Ship->GetPriorityLiveSystem() == ESkyguardPatrolShipSystem::Engines);
	TestFalse(TEXT("three kills do not defeat the ship"), Ship->IsDefeated());

	World->DestroyWorld(false);
	return true;
}

#endif
