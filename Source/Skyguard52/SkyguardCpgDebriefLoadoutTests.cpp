#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgDebrief.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardPatrolShipBoss.h"
#include "SkyguardSortiePresentationComponent.h"
#include "SkyguardSortiePresentationWidgets.h"

#include "Engine/World.h"
#include "InputCoreTypes.h"
#include "Misc/AutomationTest.h"

namespace SkyguardCpgDebriefLoadoutTests
{
	FSkyguardCpgDebriefSnapshot MakeHarborWinSnapshot()
	{
		FSkyguardCpgDebriefSnapshot Snap;
		Snap.bValid = true;
		Snap.bWon = true;
		Snap.MissionTitle = TEXT("Harbor Breaker");
		Snap.OutcomeNarrative =
			TEXT("The patrol ship is dead in the water. CPG stations held.");
		Snap.Score = 7200;
		Snap.Medal = 2;
		Snap.ShotsFired = 48;
		Snap.Hits = 12;
		Snap.CargoPercent = 80;
		Snap.bRadarDead = true;
		Snap.DestroyedSystems = {
			ESkyguardPatrolShipSystem::Radar,
			ESkyguardPatrolShipSystem::Launcher
		};
		Snap.SelectedLoadout = ESkyguardLoadout::AntiArmor;
		Snap.CannonReady = 24;
		Snap.RocketReady = 8;
		Snap.GuidedReady = 4;
		return Snap;
	}

	FSkyguardCpgDebriefSnapshot MakeHarborFailSnapshot()
	{
		FSkyguardCpgDebriefSnapshot Snap = MakeHarborWinSnapshot();
		Snap.bWon = false;
		Snap.OutcomeNarrative =
			TEXT("Cargo is gone. CPG could not hold the harbor.");
		Snap.Score = 900;
		Snap.Medal = 0;
		Snap.ShotsFired = 21;
		Snap.Hits = 4;
		Snap.CargoPercent = 0;
		Snap.DestroyedSystems = { ESkyguardPatrolShipSystem::Engines };
		Snap.SelectedLoadout = ESkyguardLoadout::RocketHeavy;
		Snap.CannonReady = 24;
		Snap.RocketReady = 20;
		Snap.GuidedReady = 1;
		return Snap;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardLoadoutOneVsTwoChangesAmmoAndStationTest,
	"Skyguard52.Apache.LoadoutOneVsTwoChangesAmmoAndStation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardLoadoutOneVsTwoChangesAmmoAndStationTest::RunTest(
	const FString& Parameters)
{
	const FSkyguardLoadoutSpec Slot1 =
		SkyguardResolveLoadout(SkyguardLoadoutFromSlot(1));
	const FSkyguardLoadoutSpec Slot2 =
		SkyguardResolveLoadout(SkyguardLoadoutFromSlot(2));
	TestEqual(
		TEXT("key 1 is Anti-Armor"),
		SkyguardLoadoutFromSlot(1),
		ESkyguardLoadout::AntiArmor);
	TestEqual(
		TEXT("key 2 is Rocket Heavy"),
		SkyguardLoadoutFromSlot(2),
		ESkyguardLoadout::RocketHeavy);
	TestTrue(
		TEXT("loadout 1 vs 2 starts on different CPG stations"),
		Slot1.StartingStation != Slot2.StartingStation);
	TestTrue(
		TEXT("loadout 1 vs 2 changes ready Hellfire count"),
		Slot1.GuidedMagazineSize != Slot2.GuidedMagazineSize);
	TestTrue(
		TEXT("loadout 1 vs 2 changes ready Hydra count"),
		Slot1.RocketMagazineSize != Slot2.RocketMagazineSize);
	TestTrue(
		TEXT("station swap is a playstyle, not a 3 percent bump"),
		FMath::Abs(Slot1.GuidedMagazineSize - Slot2.GuidedMagazineSize) >= 2 &&
			FMath::Abs(Slot1.RocketMagazineSize - Slot2.RocketMagazineSize) >= 4);

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	Gunner->ApplyLoadout(SkyguardLoadoutFromSlot(1));
	const ESkyguardGunshipWeapon Station1 = Gunner->GetSelectedGunshipWeapon();
	const int32 Guided1 = Gunner->GetGuidedAmmo();
	const int32 Rockets1 = Gunner->GetRocketAmmo();
	TestEqual(
		TEXT("slot 1 selects the Anti-Armor station"),
		Station1,
		Slot1.StartingStation);
	TestEqual(TEXT("slot 1 ready Hellfires"), Guided1, Slot1.GuidedMagazineSize);
	TestEqual(TEXT("slot 1 ready Hydras"), Rockets1, Slot1.RocketMagazineSize);

	Gunner->ApplyLoadout(SkyguardLoadoutFromSlot(2));
	TestEqual(
		TEXT("slot 2 selects the Rocket Heavy station"),
		Gunner->GetSelectedGunshipWeapon(),
		Slot2.StartingStation);
	TestEqual(
		TEXT("slot 2 ready Hellfires"),
		Gunner->GetGuidedAmmo(),
		Slot2.GuidedMagazineSize);
	TestEqual(
		TEXT("slot 2 ready Hydras"),
		Gunner->GetRocketAmmo(),
		Slot2.RocketMagazineSize);
	TestTrue(
		TEXT("1 vs 2 is not cosmetic on the gunner"),
		Gunner->GetSelectedGunshipWeapon() != Station1 &&
			(Gunner->GetGuidedAmmo() != Guided1 ||
				Gunner->GetRocketAmmo() != Rockets1));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgDebriefCopyIsCleanWithCombatAndShipSystemsTest,
	"Skyguard52.Presentation.Sortie.CpgDebriefCopyIsCleanWithCombatAndSystems",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgDebriefCopyIsCleanWithCombatAndShipSystemsTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardCpgDebriefLoadoutTests;
	const FString Win = SkyguardBuildCpgDebriefCopy(MakeHarborWinSnapshot());
	const FString Fail = SkyguardBuildCpgDebriefCopy(MakeHarborFailSnapshot());

	TestFalse(TEXT("win debrief bans Igla/Yak/rifle"), SkyguardCpgCopyHasBannedTerm(Win));
	TestFalse(TEXT("fail debrief bans Igla/Yak/rifle"), SkyguardCpgCopyHasBannedTerm(Fail));
	TestTrue(TEXT("win names the CPG seat"), Win.Contains(TEXT("CPG")));
	TestTrue(TEXT("fail names the CPG seat"), Fail.Contains(TEXT("CPG")));
	TestTrue(
		TEXT("win lists 30 mm / Hydra / Hellfire stations"),
		Win.Contains(TEXT("30 mm")) &&
			Win.Contains(TEXT("Hydra")) &&
			Win.Contains(TEXT("Hellfire")));
	TestTrue(TEXT("win shows fired count"), Win.Contains(TEXT("48")));
	TestTrue(TEXT("win shows hit count"), Win.Contains(TEXT("12")));
	TestTrue(
		TEXT("win lists stripped search radar"),
		Win.Contains(TEXT("Search Radar")));
	TestTrue(
		TEXT("win lists stripped launcher"),
		Win.Contains(TEXT("Launcher")));
	TestTrue(
		TEXT("fail lists stripped engines"),
		Fail.Contains(TEXT("Engines")));
	TestTrue(TEXT("win is a WIN line"), Win.Contains(TEXT("WIN")));
	TestTrue(TEXT("fail is a FAIL line"), Fail.Contains(TEXT("FAIL")));
	TestTrue(
		TEXT("continue hint is N or Enter"),
		Win.Contains(TEXT("N / Enter")) && Fail.Contains(TEXT("N / Enter")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgDebriefKeysSelectLoadoutAndContinueAdvancesTest,
	"Skyguard52.Presentation.Sortie.CpgDebriefKeysSelectLoadoutAndContinueAdvances",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgDebriefKeysSelectLoadoutAndContinueAdvancesTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardCpgDebriefWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	ASkyguardPatrolShipBoss* Ship =
		World->SpawnActor<ASkyguardPatrolShipBoss>();
	USkyguardSortiePresentationComponent* Presentation =
		NewObject<USkyguardSortiePresentationComponent>(GetTransientPackage());
	TestNotNull(TEXT("director"), Director);
	TestNotNull(TEXT("gunner"), Gunner);
	TestNotNull(TEXT("ship"), Ship);
	TestNotNull(TEXT("presentation"), Presentation);
	if (!Director || !Gunner || !Ship || !Presentation)
	{
		World->DestroyWorld(false);
		return false;
	}

	Director->bAutoStart = false;
	Director->StartMissionIndex(1);
	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Radar, 500.f);
	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Launcher, 500.f);
	Gunner->RecordRifleShot();
	Gunner->RecordRifleShot();
	Gunner->RecordRifleHit();
	Director->ResolveSortie(true);

	Presentation->BindGunshipDirector(Director);
	Presentation->CaptureCpgDebrief(Director, Gunner, Ship);
	TestTrue(TEXT("CPG debrief is armed"), Presentation->HasCpgDebrief());
	TestEqual(
		TEXT("debrief is ready"),
		Presentation->GetPresentationState(),
		ESkyguardSortiePresentationState::DebriefReady);

	const FString Captured = Presentation->GetCpgDebriefCopy().ToString();
	TestFalse(
		TEXT("captured debrief bans Igla/Yak/rifle"),
		SkyguardCpgCopyHasBannedTerm(Captured));
	TestTrue(TEXT("captured debrief names CPG"), Captured.Contains(TEXT("CPG")));
	TestTrue(
		TEXT("captured debrief lists stripped radar"),
		Captured.Contains(TEXT("Search Radar")));
	TestTrue(
		TEXT("captured debrief lists stripped launcher"),
		Captured.Contains(TEXT("Launcher")));
	TestTrue(TEXT("captured debrief shows shots"), Captured.Contains(TEXT("2")));
	TestTrue(TEXT("captured debrief shows hits"), Captured.Contains(TEXT("1")));

	USkyguardDebriefWidget* Widget = NewObject<USkyguardDebriefWidget>();
	Widget->Configure(Presentation);
	const FString WidgetCopy = Widget->GetDebriefNarrative().ToString();
	TestFalse(
		TEXT("widget debrief bans Igla/Yak/rifle"),
		SkyguardCpgCopyHasBannedTerm(WidgetCopy));
	TestTrue(TEXT("widget shows CPG copy"), WidgetCopy.Contains(TEXT("CPG")));

	TestTrue(
		TEXT("key 1 selects Anti-Armor"),
		Presentation->HandleDebriefKey(EKeys::One));
	TestEqual(
		TEXT("director pending is Anti-Armor"),
		Director->GetPendingLoadout(),
		ESkyguardLoadout::AntiArmor);
	TestEqual(
		TEXT("key 1 is not cosmetic — Hellfire station is live"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::GuidedMissile);
	const int32 GuidedAntiArmor = Gunner->GetGuidedAmmo();
	const int32 RocketsAntiArmor = Gunner->GetRocketAmmo();

	TestTrue(
		TEXT("key 2 selects Rocket Heavy"),
		Presentation->HandleDebriefKey(EKeys::Two));
	TestEqual(
		TEXT("director pending is Rocket Heavy"),
		Director->GetPendingLoadout(),
		ESkyguardLoadout::RocketHeavy);
	TestEqual(
		TEXT("key 2 is not cosmetic — Hydra station is live"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::Rockets);
	TestTrue(
		TEXT("key 1 vs 2 changes ready ammo"),
		Gunner->GetGuidedAmmo() != GuidedAntiArmor ||
			Gunner->GetRocketAmmo() != RocketsAntiArmor);

	TestTrue(
		TEXT("Enter continues the campaign"),
		Presentation->HandleDebriefKey(EKeys::Enter));
	TestEqual(
		TEXT("win continue advances Harbor Breaker to the next sortie"),
		Director->GetMissionIndex(),
		2);
	TestFalse(
		TEXT("continue leaves debrief"),
		Director->IsAwaitingContinue());

	Director->StartMissionIndex(1);
	Director->ResolveSortie(false);
	Presentation->CaptureCpgDebrief(Director, Gunner, Ship);
	const FString FailCopy = Presentation->GetCpgDebriefCopy().ToString();
	TestFalse(
		TEXT("fail debrief bans Igla/Yak/rifle"),
		SkyguardCpgCopyHasBannedTerm(FailCopy));
	TestTrue(TEXT("fail debrief is FAIL"), FailCopy.Contains(TEXT("FAIL")));
	TestTrue(
		TEXT("N continues a failed sortie"),
		Presentation->HandleDebriefKey(EKeys::N));
	TestEqual(
		TEXT("fail continue retries Harbor Breaker"),
		Director->GetMissionIndex(),
		1);
	TestFalse(
		TEXT("retry leaves debrief"),
		Director->IsAwaitingContinue());

	World->DestroyWorld(false);
	return true;
}

#endif
