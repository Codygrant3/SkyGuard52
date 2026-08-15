#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgHud.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardPatrolShipBoss.h"
#include "Components/PrimitiveComponent.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace
{
	bool CopyHasBannedTerm(const FString& Text)
	{
		const FString Lower = Text.ToLower();
		return Lower.Contains(TEXT("igla")) ||
			Lower.Contains(TEXT("yak")) ||
			Lower.Contains(TEXT("rifle"));
	}

	void KillSystem(ASkyguardPatrolShipBoss* Ship, const ESkyguardPatrolShipSystem System)
	{
		Ship->ApplyHitToSystem(System, 500.f);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPatrolShipSystemsChangeTheFightTest,
	"Skyguard52.Campaign.PatrolShipSystemsChangeTheFight",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPatrolShipSystemsChangeTheFightTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardShipSystemsWorld"));
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

	TestTrue(TEXT("radar coordinates ADA"), Ship->CanCoordinateAda());
	TestTrue(TEXT("launcher can inbound"), Ship->CanLaunchInbound());
	TestTrue(TEXT("cannon threatens"), Ship->GetCannonThreatDamage() > 0.f);
	TestTrue(TEXT("deck can launch"), Ship->CanLaunchDrones());
	TestTrue(TEXT("engines make way"), Ship->GetUnderwaySpeed() > 0.f);

	const FVector Start = Ship->GetActorLocation();
	Ship->Tick(1.f);
	TestTrue(
		TEXT("live engines move the hull"),
		FVector::DistSquared(Start, Ship->GetActorLocation()) > 1.f);

	Ship->ApplyHit(nullptr, 500.f);
	TestEqual(
		TEXT("nullptr hull splash kills no system"),
		Ship->GetDestroyedSystemCount(),
		0);
	TestTrue(TEXT("hull splash leaves radar coordinating"), Ship->CanCoordinateAda());

	UPrimitiveComponent* Radar = Ship->GetSystemComponent(
		ESkyguardPatrolShipSystem::Radar);
	TestNotNull(TEXT("radar mesh"), Radar);
	Ship->ApplyHit(Radar, 500.f);
	TestTrue(TEXT("radar component is dead"), Ship->IsRadarDead());
	TestFalse(TEXT("radar down kills ADA coordination"), Ship->CanCoordinateAda());
	TestTrue(TEXT("radar down leaves the launcher live"), Ship->CanLaunchInbound());
	TestEqual(TEXT("one system down"), Ship->GetDestroyedSystemCount(), 1);
	TestFalse(TEXT("one system is not a dead ship"), Ship->IsDefeated());

	KillSystem(Ship, ESkyguardPatrolShipSystem::Launcher);
	TestFalse(TEXT("launcher down stays cold"), Ship->CanLaunchInbound());

	KillSystem(Ship, ESkyguardPatrolShipSystem::Cannon);
	TestEqual(TEXT("cannon down is no threat"), Ship->GetCannonThreatDamage(), 0.0);

	KillSystem(Ship, ESkyguardPatrolShipSystem::Engines);
	TestEqual(TEXT("engines down stop the hull"), Ship->GetUnderwaySpeed(), 0.0);
	const FVector Stopped = Ship->GetActorLocation();
	Ship->Tick(1.f);
	TestTrue(
		TEXT("dead engines hold position"),
		FVector::DistSquared(Stopped, Ship->GetActorLocation()) < 1.f);

	TestTrue(
		TEXT("deck still launches before it is hit"),
		Ship->ConsumeDeckLaunch(ASkyguardPatrolShipBoss::DeckLaunchIntervalSeconds));
	KillSystem(Ship, ESkyguardPatrolShipSystem::DroneDeck);
	TestFalse(TEXT("deck down cannot launch"), Ship->CanLaunchDrones());
	TestFalse(
		TEXT("deck down consumes no launch"),
		Ship->ConsumeDeckLaunch(ASkyguardPatrolShipBoss::DeckLaunchIntervalSeconds));

	TestTrue(TEXT("four-plus systems defeat the ship"), Ship->IsDefeated());
	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPatrolShipHudNamesSystemsTest,
	"Skyguard52.Campaign.PatrolShipHudNamesSystems",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPatrolShipHudNamesSystemsTest::RunTest(const FString& Parameters)
{
	ASkyguardPatrolShipBoss* Ship = NewObject<ASkyguardPatrolShipBoss>();
	TestNotNull(TEXT("ship"), Ship);
	if (!Ship)
	{
		return false;
	}

	const FString Line = Ship->GetHudSystemLine();
	TestTrue(TEXT("tape names RADAR"), Line.Contains(TEXT("RADAR")));
	TestTrue(TEXT("tape names GUN"), Line.Contains(TEXT("GUN")));
	TestTrue(TEXT("tape names LNCH"), Line.Contains(TEXT("LNCH")));
	TestTrue(TEXT("tape names ENG"), Line.Contains(TEXT("ENG")));
	TestTrue(TEXT("tape names DECK"), Line.Contains(TEXT("DECK")));
	TestFalse(TEXT("system tape bans Igla/Yak/rifle"), CopyHasBannedTerm(Line));
	TestTrue(
		TEXT("priority live system is radar"),
		Ship->GetPriorityLiveSystem() == ESkyguardPatrolShipSystem::Radar);
	TestEqual(
		TEXT("radar label"),
		FString(SkyguardCpgShipSystemLabel(ESkyguardPatrolShipSystem::Radar)),
		FString(TEXT("RADAR")));
	TestEqual(
		TEXT("cannon label"),
		FString(SkyguardCpgShipSystemLabel(ESkyguardPatrolShipSystem::Cannon)),
		FString(TEXT("GUN")));
	TestEqual(
		TEXT("launcher label"),
		FString(SkyguardCpgShipSystemLabel(ESkyguardPatrolShipSystem::Launcher)),
		FString(TEXT("LNCH")));

	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Radar, 500.f);
	const FString AfterRadar = Ship->GetHudSystemLine();
	TestTrue(TEXT("dead radar is marked"), AfterRadar.Contains(TEXT("XRADAR")));
	TestTrue(
		TEXT("next priority is cannon"),
		Ship->GetPriorityLiveSystem() == ESkyguardPatrolShipSystem::Cannon);
	TestFalse(TEXT("marked tape still bans Igla/Yak/rifle"), CopyHasBannedTerm(AfterRadar));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPatrolShipHudShowsSystemsOnTapeTest,
	"Skyguard52.Campaign.PatrolShipHudShowsSystemsOnTape",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPatrolShipHudShowsSystemsOnTapeTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardShipHudWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>(
		FVector::ZeroVector,
		FRotator::ZeroRotator);
	ASkyguardPatrolShipBoss* Ship = World->SpawnActor<ASkyguardPatrolShipBoss>(
		FVector(2000.f, 0.f, 0.f),
		FRotator::ZeroRotator);
	TestNotNull(TEXT("gunner"), Gunner);
	TestNotNull(TEXT("ship"), Ship);
	if (!Gunner || !Ship)
	{
		World->DestroyWorld(false);
		return false;
	}

	const FSkyguardCpgHudSnapshot Snap = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("ship is a contact"), Snap.ThreatCount >= 1);
	TestTrue(TEXT("threat tape names RADAR"), Snap.ThreatLine.Contains(TEXT("RADAR")));
	TestTrue(TEXT("threat tape names GUN"), Snap.ThreatLine.Contains(TEXT("GUN")));
	TestTrue(TEXT("threat tape names LNCH"), Snap.ThreatLine.Contains(TEXT("LNCH")));
	TestTrue(TEXT("threat tape names ENG"), Snap.ThreatLine.Contains(TEXT("ENG")));
	TestTrue(TEXT("threat tape names DECK"), Snap.ThreatLine.Contains(TEXT("DECK")));
	TestFalse(TEXT("threat tape bans Igla/Yak/rifle"), CopyHasBannedTerm(Snap.ThreatLine));

	TArray<FSkyguardCpgContactMark> Marks;
	Gunner->CollectCpgContactMarks(Marks);
	bool bNamedSystem = false;
	for (const FSkyguardCpgContactMark& Mark : Marks)
	{
		if (Mark.Label == TEXT("RADAR") ||
			Mark.Label == TEXT("GUN") ||
			Mark.Label == TEXT("LNCH") ||
			Mark.Label == TEXT("ENG") ||
			Mark.Label == TEXT("DECK"))
		{
			bNamedSystem = true;
		}
		TestFalse(TEXT("contact mark bans Igla/Yak/rifle"), CopyHasBannedTerm(Mark.Label));
	}
	TestTrue(TEXT("contact mark names a ship system"), bNamedSystem);

	World->DestroyWorld(false);
	return true;
}

#endif
