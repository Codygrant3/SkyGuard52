#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGunshipTypes.h"

#include "Misc/AutomationTest.h"

// Isolated public-API lock for SkyguardGunshipTypes loadout helpers.
// No Gunner spawn, no world, no ApplyWeaponHit.

namespace SkyguardGunshipTypesLoadoutTests
{
	bool PlaystyleHasBannedTerm(const TCHAR* Line)
	{
		const FString Lower = FString(Line).ToLower();
		return Lower.Contains(TEXT("igla")) ||
			Lower.Contains(TEXT("yak")) ||
			Lower.Contains(TEXT("rifle"));
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGunshipTypesLoadoutSlotRoundTripTest,
	"Skyguard52.Apache.Loadout.SlotRoundTripAndDefaultBranch",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGunshipTypesLoadoutSlotRoundTripTest::RunTest(
	const FString& Parameters)
{
	TestEqual(
		TEXT("slot 1 is AntiArmor"),
		SkyguardLoadoutFromSlot(1),
		ESkyguardLoadout::AntiArmor);
	TestEqual(
		TEXT("slot 2 is RocketHeavy"),
		SkyguardLoadoutFromSlot(2),
		ESkyguardLoadout::RocketHeavy);
	TestEqual(
		TEXT("slot 3 is Intercept"),
		SkyguardLoadoutFromSlot(3),
		ESkyguardLoadout::Intercept);
	TestEqual(
		TEXT("slot 4 is Balanced"),
		SkyguardLoadoutFromSlot(4),
		ESkyguardLoadout::Balanced);
	TestEqual(
		TEXT("slot 0 follows the default branch (Balanced)"),
		SkyguardLoadoutFromSlot(0),
		ESkyguardLoadout::Balanced);
	TestEqual(
		TEXT("slot 5 follows the default branch (Balanced)"),
		SkyguardLoadoutFromSlot(5),
		ESkyguardLoadout::Balanced);

	TestEqual(
		TEXT("AntiArmor occupies slot 1"),
		SkyguardLoadoutSlot(ESkyguardLoadout::AntiArmor),
		1);
	TestEqual(
		TEXT("RocketHeavy occupies slot 2"),
		SkyguardLoadoutSlot(ESkyguardLoadout::RocketHeavy),
		2);
	TestEqual(
		TEXT("Intercept occupies slot 3"),
		SkyguardLoadoutSlot(ESkyguardLoadout::Intercept),
		3);
	TestEqual(
		TEXT("Balanced occupies slot 4"),
		SkyguardLoadoutSlot(ESkyguardLoadout::Balanced),
		4);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGunshipTypesLoadoutDisplayNameTest,
	"Skyguard52.Apache.Loadout.DisplayNames",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGunshipTypesLoadoutDisplayNameTest::RunTest(
	const FString& Parameters)
{
	TestEqual(
		TEXT("AntiArmor display name"),
		FString(SkyguardLoadoutDisplayName(ESkyguardLoadout::AntiArmor)),
		FString(TEXT("Anti-Armor")));
	TestEqual(
		TEXT("RocketHeavy display name"),
		FString(SkyguardLoadoutDisplayName(ESkyguardLoadout::RocketHeavy)),
		FString(TEXT("Rocket Heavy")));
	TestEqual(
		TEXT("Intercept display name"),
		FString(SkyguardLoadoutDisplayName(ESkyguardLoadout::Intercept)),
		FString(TEXT("Intercept")));
	TestEqual(
		TEXT("Balanced display name"),
		FString(SkyguardLoadoutDisplayName(ESkyguardLoadout::Balanced)),
		FString(TEXT("Balanced")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGunshipTypesResolveLoadoutMatchesImplementationTest,
	"Skyguard52.Apache.Loadout.ResolveMatchesImplementation",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGunshipTypesResolveLoadoutMatchesImplementationTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardGunshipTypesLoadoutTests;

	TestEqual(
		TEXT("Balanced feel cannon magazine is 30"),
		SkyguardApacheCpgFeel::CannonMagazineSize,
		30);
	TestEqual(
		TEXT("Balanced feel rocket magazine is 14"),
		SkyguardApacheCpgFeel::RocketMagazineSize,
		14);
	TestEqual(
		TEXT("Balanced feel guided magazine is 2"),
		SkyguardApacheCpgFeel::GuidedMagazineSize,
		2);

	const FSkyguardLoadoutSpec AntiArmor =
		SkyguardResolveLoadout(ESkyguardLoadout::AntiArmor);
	TestEqual(
		TEXT("AntiArmor loadout id"),
		AntiArmor.Loadout,
		ESkyguardLoadout::AntiArmor);
	TestEqual(
		TEXT("AntiArmor starts GuidedMissile"),
		AntiArmor.StartingStation,
		ESkyguardGunshipWeapon::GuidedMissile);
	TestEqual(TEXT("AntiArmor cannon magazine"), AntiArmor.CannonMagazineSize, 24);
	TestEqual(TEXT("AntiArmor rocket magazine"), AntiArmor.RocketMagazineSize, 8);
	TestEqual(TEXT("AntiArmor guided magazine"), AntiArmor.GuidedMagazineSize, 4);
	TestEqual(TEXT("AntiArmor flare count"), AntiArmor.FlareCount, 8);
	TestEqual(TEXT("AntiArmor hull integrity"), AntiArmor.HullIntegrity, 120.f);
	TestEqual(
		TEXT("AntiArmor playstyle line"),
		FString(AntiArmor.PlaystyleLine),
		FString(TEXT("Hellfire station, extra guided missiles")));

	const FSkyguardLoadoutSpec RocketHeavy =
		SkyguardResolveLoadout(ESkyguardLoadout::RocketHeavy);
	TestEqual(
		TEXT("RocketHeavy loadout id"),
		RocketHeavy.Loadout,
		ESkyguardLoadout::RocketHeavy);
	TestEqual(
		TEXT("RocketHeavy starts Rockets"),
		RocketHeavy.StartingStation,
		ESkyguardGunshipWeapon::Rockets);
	TestEqual(TEXT("RocketHeavy cannon magazine"), RocketHeavy.CannonMagazineSize, 24);
	TestEqual(TEXT("RocketHeavy rocket magazine"), RocketHeavy.RocketMagazineSize, 20);
	TestEqual(TEXT("RocketHeavy guided magazine"), RocketHeavy.GuidedMagazineSize, 1);
	TestEqual(TEXT("RocketHeavy flare count"), RocketHeavy.FlareCount, 5);
	TestEqual(TEXT("RocketHeavy hull integrity"), RocketHeavy.HullIntegrity, 140.f);
	TestEqual(
		TEXT("RocketHeavy playstyle line"),
		FString(RocketHeavy.PlaystyleLine),
		FString(TEXT("Hydra station, extra rockets")));

	const FSkyguardLoadoutSpec Intercept =
		SkyguardResolveLoadout(ESkyguardLoadout::Intercept);
	TestEqual(
		TEXT("Intercept loadout id"),
		Intercept.Loadout,
		ESkyguardLoadout::Intercept);
	TestEqual(
		TEXT("Intercept starts Cannon"),
		Intercept.StartingStation,
		ESkyguardGunshipWeapon::Cannon);
	TestEqual(TEXT("Intercept cannon magazine"), Intercept.CannonMagazineSize, 40);
	TestEqual(TEXT("Intercept rocket magazine"), Intercept.RocketMagazineSize, 8);
	TestEqual(TEXT("Intercept guided magazine"), Intercept.GuidedMagazineSize, 1);
	TestEqual(TEXT("Intercept flare count"), Intercept.FlareCount, 10);
	TestEqual(TEXT("Intercept hull integrity"), Intercept.HullIntegrity, 170.f);
	TestEqual(
		TEXT("Intercept playstyle line"),
		FString(Intercept.PlaystyleLine),
		FString(TEXT("30 mm station, extra cannon and flares")));

	const FSkyguardLoadoutSpec Balanced =
		SkyguardResolveLoadout(ESkyguardLoadout::Balanced);
	TestEqual(
		TEXT("Balanced loadout id"),
		Balanced.Loadout,
		ESkyguardLoadout::Balanced);
	TestEqual(
		TEXT("Balanced starts Cannon"),
		Balanced.StartingStation,
		ESkyguardGunshipWeapon::Cannon);
	TestEqual(
		TEXT("Balanced cannon magazine uses CPG feel"),
		Balanced.CannonMagazineSize,
		SkyguardApacheCpgFeel::CannonMagazineSize);
	TestEqual(
		TEXT("Balanced rocket magazine uses CPG feel"),
		Balanced.RocketMagazineSize,
		SkyguardApacheCpgFeel::RocketMagazineSize);
	TestEqual(
		TEXT("Balanced guided magazine uses CPG feel"),
		Balanced.GuidedMagazineSize,
		SkyguardApacheCpgFeel::GuidedMagazineSize);
	TestEqual(TEXT("Balanced flare count"), Balanced.FlareCount, 6);
	TestEqual(TEXT("Balanced hull integrity"), Balanced.HullIntegrity, 140.f);
	TestEqual(
		TEXT("Balanced playstyle line"),
		FString(Balanced.PlaystyleLine),
		FString(TEXT("30 mm station, mixed cannon, rockets, missiles")));

	const ESkyguardLoadout NamedLoadouts[] = {
		ESkyguardLoadout::AntiArmor,
		ESkyguardLoadout::RocketHeavy,
		ESkyguardLoadout::Intercept,
		ESkyguardLoadout::Balanced
	};
	for (const ESkyguardLoadout Loadout : NamedLoadouts)
	{
		const FSkyguardLoadoutSpec Spec = SkyguardResolveLoadout(Loadout);
		TestFalse(
			*FString::Printf(
				TEXT("%s playstyle bans Igla/Yak/rifle"),
				SkyguardLoadoutDisplayName(Loadout)),
			PlaystyleHasBannedTerm(Spec.PlaystyleLine));
	}
	return true;
}

#endif
