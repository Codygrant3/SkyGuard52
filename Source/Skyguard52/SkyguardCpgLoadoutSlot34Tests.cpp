#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGunner.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardSortiePresentationComponent.h"

#include "Engine/World.h"
#include "InputCoreTypes.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardLoadoutThreeVsFourChangesAmmoAndStationTest,
	"Skyguard52.Apache.LoadoutThreeVsFourChangesAmmoAndStation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardLoadoutThreeVsFourChangesAmmoAndStationTest::RunTest(
	const FString& Parameters)
{
	const FSkyguardLoadoutSpec Slot3 =
		SkyguardResolveLoadout(SkyguardLoadoutFromSlot(3));
	const FSkyguardLoadoutSpec Slot4 =
		SkyguardResolveLoadout(SkyguardLoadoutFromSlot(4));
	TestEqual(
		TEXT("key 3 is Intercept"),
		SkyguardLoadoutFromSlot(3),
		ESkyguardLoadout::Intercept);
	TestEqual(
		TEXT("key 4 is Balanced"),
		SkyguardLoadoutFromSlot(4),
		ESkyguardLoadout::Balanced);
	TestEqual(
		TEXT("Intercept occupies slot 3"),
		SkyguardLoadoutSlot(ESkyguardLoadout::Intercept),
		3);
	TestEqual(
		TEXT("Balanced occupies slot 4"),
		SkyguardLoadoutSlot(ESkyguardLoadout::Balanced),
		4);
	TestEqual(
		TEXT("slot 3 named loadout id is Intercept"),
		Slot3.Loadout,
		ESkyguardLoadout::Intercept);
	TestEqual(
		TEXT("slot 4 named loadout id is Balanced"),
		Slot4.Loadout,
		ESkyguardLoadout::Balanced);
	TestTrue(
		TEXT("loadout 3 vs 4 changes ready 30 mm count"),
		Slot3.CannonMagazineSize != Slot4.CannonMagazineSize);
	TestTrue(
		TEXT("loadout 3 vs 4 changes ready Hydra count"),
		Slot3.RocketMagazineSize != Slot4.RocketMagazineSize);
	TestTrue(
		TEXT("loadout 3 vs 4 changes ready Hellfire count"),
		Slot3.GuidedMagazineSize != Slot4.GuidedMagazineSize);
	TestTrue(
		TEXT("Intercept vs Balanced is a playstyle, not a 3 percent bump"),
		FMath::Abs(Slot3.CannonMagazineSize - Slot4.CannonMagazineSize) >= 8 &&
			FMath::Abs(Slot3.RocketMagazineSize - Slot4.RocketMagazineSize) >= 4);

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	Gunner->ApplyLoadout(SkyguardLoadoutFromSlot(3));
	const int32 Cannon3 = Gunner->GetCannonMagazine();
	const int32 Guided3 = Gunner->GetGuidedAmmo();
	const int32 Rockets3 = Gunner->GetRocketAmmo();
	TestEqual(
		TEXT("slot 3 applies the Intercept loadout"),
		Gunner->GetActiveLoadout(),
		ESkyguardLoadout::Intercept);
	TestEqual(
		TEXT("slot 3 selects the Intercept station"),
		Gunner->GetSelectedGunshipWeapon(),
		Slot3.StartingStation);
	TestEqual(TEXT("slot 3 ready 30 mm"), Cannon3, Slot3.CannonMagazineSize);
	TestEqual(TEXT("slot 3 ready Hellfires"), Guided3, Slot3.GuidedMagazineSize);
	TestEqual(TEXT("slot 3 ready Hydras"), Rockets3, Slot3.RocketMagazineSize);

	Gunner->ApplyLoadout(SkyguardLoadoutFromSlot(4));
	TestEqual(
		TEXT("slot 4 applies the Balanced loadout"),
		Gunner->GetActiveLoadout(),
		ESkyguardLoadout::Balanced);
	TestEqual(
		TEXT("slot 4 selects the Balanced station"),
		Gunner->GetSelectedGunshipWeapon(),
		Slot4.StartingStation);
	TestEqual(
		TEXT("slot 4 ready 30 mm"),
		Gunner->GetCannonMagazine(),
		Slot4.CannonMagazineSize);
	TestEqual(
		TEXT("slot 4 ready Hellfires"),
		Gunner->GetGuidedAmmo(),
		Slot4.GuidedMagazineSize);
	TestEqual(
		TEXT("slot 4 ready Hydras"),
		Gunner->GetRocketAmmo(),
		Slot4.RocketMagazineSize);
	TestTrue(
		TEXT("3 vs 4 is not cosmetic on the gunner"),
		Gunner->GetActiveLoadout() != ESkyguardLoadout::Intercept &&
			(Gunner->GetCannonMagazine() != Cannon3 ||
				Gunner->GetGuidedAmmo() != Guided3 ||
				Gunner->GetRocketAmmo() != Rockets3));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgDebriefKeysThreeAndFourSelectLoadoutTest,
	"Skyguard52.Presentation.Sortie.CpgDebriefKeysThreeAndFourSelectLoadout",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgDebriefKeysThreeAndFourSelectLoadoutTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardCpgLoadoutSlot34World"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	USkyguardSortiePresentationComponent* Presentation =
		NewObject<USkyguardSortiePresentationComponent>(GetTransientPackage());
	TestNotNull(TEXT("director"), Director);
	TestNotNull(TEXT("gunner"), Gunner);
	TestNotNull(TEXT("presentation"), Presentation);
	if (!Director || !Gunner || !Presentation)
	{
		World->DestroyWorld(false);
		return false;
	}

	Director->bAutoStart = false;
	Presentation->BindGunshipDirector(Director);
	Presentation->CaptureCpgDebrief(Director, Gunner, nullptr);
	TestTrue(
		TEXT("slot 3 select API maps to Intercept"),
		Presentation->SelectLoadoutSlot(3));
	TestEqual(
		TEXT("select slot 3 pending is Intercept"),
		Director->GetPendingLoadout(),
		ESkyguardLoadout::Intercept);
	TestEqual(
		TEXT("select slot 3 presentation is Intercept"),
		Presentation->GetSelectedLoadout(),
		ESkyguardLoadout::Intercept);

	TestTrue(
		TEXT("key 3 selects Intercept"),
		Presentation->HandleDebriefKey(EKeys::Three));
	TestEqual(
		TEXT("director pending is Intercept"),
		Director->GetPendingLoadout(),
		ESkyguardLoadout::Intercept);
	TestEqual(
		TEXT("key 3 applies Intercept on the gunner"),
		Gunner->GetActiveLoadout(),
		ESkyguardLoadout::Intercept);
	const FSkyguardLoadoutSpec Intercept =
		SkyguardResolveLoadout(ESkyguardLoadout::Intercept);
	TestEqual(
		TEXT("key 3 is not cosmetic — Intercept 30 mm is live"),
		Gunner->GetCannonMagazine(),
		Intercept.CannonMagazineSize);
	TestEqual(
		TEXT("key 3 ready Hydras"),
		Gunner->GetRocketAmmo(),
		Intercept.RocketMagazineSize);
	TestEqual(
		TEXT("key 3 ready Hellfires"),
		Gunner->GetGuidedAmmo(),
		Intercept.GuidedMagazineSize);
	const int32 CannonIntercept = Gunner->GetCannonMagazine();
	const int32 RocketsIntercept = Gunner->GetRocketAmmo();
	const int32 GuidedIntercept = Gunner->GetGuidedAmmo();

	TestTrue(
		TEXT("slot 4 select API maps to Balanced"),
		Presentation->SelectLoadoutSlot(4));
	TestEqual(
		TEXT("select slot 4 pending is Balanced"),
		Director->GetPendingLoadout(),
		ESkyguardLoadout::Balanced);

	TestTrue(
		TEXT("key 4 selects Balanced"),
		Presentation->HandleDebriefKey(EKeys::Four));
	TestEqual(
		TEXT("director pending is Balanced"),
		Director->GetPendingLoadout(),
		ESkyguardLoadout::Balanced);
	TestEqual(
		TEXT("key 4 applies Balanced on the gunner"),
		Gunner->GetActiveLoadout(),
		ESkyguardLoadout::Balanced);
	const FSkyguardLoadoutSpec Balanced =
		SkyguardResolveLoadout(ESkyguardLoadout::Balanced);
	TestEqual(
		TEXT("key 4 is not cosmetic — Balanced 30 mm is live"),
		Gunner->GetCannonMagazine(),
		Balanced.CannonMagazineSize);
	TestEqual(
		TEXT("key 4 ready Hydras"),
		Gunner->GetRocketAmmo(),
		Balanced.RocketMagazineSize);
	TestEqual(
		TEXT("key 4 ready Hellfires"),
		Gunner->GetGuidedAmmo(),
		Balanced.GuidedMagazineSize);
	TestTrue(
		TEXT("key 3 vs 4 changes ready ammo"),
		Gunner->GetCannonMagazine() != CannonIntercept ||
			Gunner->GetRocketAmmo() != RocketsIntercept ||
			Gunner->GetGuidedAmmo() != GuidedIntercept);

	World->DestroyWorld(false);
	return true;
}

#endif
