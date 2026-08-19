#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgHud.h"
#include "SkyguardApacheAircraft.h"
#include "SkyguardBossTypes.h"
#include "SkyguardDrone.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardPilotVoice.h"
#include "SkyguardThreatTypes.h"
#include "Engine/World.h"
#include "GameFramework/InputSettings.h"
#include "InputCoreTypes.h"
#include "Misc/AutomationTest.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgHudTapesWeaponRangeThreatTest,
	"Skyguard52.Apache.CpgHudTapesWeaponRangeThreat",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgHudTapesWeaponRangeThreatTest::RunTest(const FString& Parameters)
{
	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	FSkyguardCpgHudSnapshot Cannon = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("cannon tape names 30 mm"), Cannon.WeaponLine.Contains(TEXT("30MM")));
	TestTrue(TEXT("cannon tape shows ready"), Cannon.WeaponLine.Contains(TEXT("RDY")));
	TestTrue(TEXT("empty world is clear"), Cannon.ThreatLine.Contains(TEXT("CLR")));
	TestTrue(TEXT("no range without a camera hit"), Cannon.RangeLine.Contains(TEXT("----")));
	TestEqual(TEXT("no contacts"), Cannon.ThreatCount, 0);
	TestFalse(
		TEXT("cannon tape is not a Yak/Igla/rifle label"),
		SkyguardCpgHudHasLegacyLiveWording(Cannon.WeaponLine));

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	FSkyguardCpgHudSnapshot Rockets = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("rocket tape names rockets"), Rockets.WeaponLine.Contains(TEXT("RKT")));
	TestFalse(
		TEXT("rocket tape is not a Yak/Igla/rifle label"),
		SkyguardCpgHudHasLegacyLiveWording(Rockets.WeaponLine));

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
	FSkyguardCpgHudSnapshot Missile = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("missile tape names guided missiles"), Missile.WeaponLine.Contains(TEXT("MSL")));
	TestTrue(TEXT("missile tape shows search before lock"), Missile.WeaponLine.Contains(TEXT("SRCH")));
	TestTrue(TEXT("eufd carries the station"), Missile.EufdLine.Contains(TEXT("MSL")));
	TestTrue(TEXT("eufd carries lock state"), Missile.EufdLine.Contains(TEXT("SRCH")));
	TestTrue(TEXT("eufd names helmet-sight"), Missile.EufdLine.Contains(TEXT("HMD")));
	TestEqual(
		TEXT("open seeker is search"),
		Missile.LockPhase,
		ESkyguardGuidedLockPhase::Search);
	TestEqual(
		TEXT("default sight is helmet"),
		Missile.SightMode,
		ESkyguardCpgSightMode::Helmet);
	TestFalse(
		TEXT("missile tape is not a Yak/Igla/rifle label"),
		SkyguardCpgHudHasLegacyLiveWording(Missile.WeaponLine + Missile.EufdLine + Missile.LockLine));

	Gunner->SelectGunshipWeapon(ESkyguardGunshipWeapon::Cannon);
	Gunner->ReloadSelectedWeapon();
	FSkyguardCpgHudSnapshot Reload = Gunner->BuildCpgHudSnapshot();
	TestTrue(
		TEXT("full magazine does not start a reload"),
		Reload.WeaponLine.Contains(TEXT("RDY")));

	TestEqual(
		TEXT("weapon label helper"),
		FString(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::Rockets)),
		FString(TEXT("RKT")));
	TestEqual(
		TEXT("cannon label helper"),
		FString(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::Cannon)),
		FString(TEXT("30MM")));
	TestEqual(
		TEXT("missile label helper"),
		FString(SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon::GuidedMissile)),
		FString(TEXT("MSL")));
	TestTrue(
		TEXT("legacy Igla wording is rejected"),
		SkyguardCpgHudHasLegacyLiveWording(FString(TEXT("Igla"))));
	TestTrue(
		TEXT("legacy Yak wording is rejected"),
		SkyguardCpgHudHasLegacyLiveWording(FString(TEXT("Yak-52"))));
	TestTrue(
		TEXT("legacy rifle wording is rejected"),
		SkyguardCpgHudHasLegacyLiveWording(FString(TEXT("rear rifle"))));
	TestFalse(
		TEXT("live station labels are clean"),
		SkyguardCpgHudHasLegacyLiveWording(FString(TEXT("30MM RKT MSL LCK"))));
	TestEqual(
		TEXT("threat label helper"),
		FString(SkyguardCpgThreatLabel(ESkyguardThreatKind::GroundArmor)),
		FString(TEXT("ARM")));
	TestEqual(
		TEXT("ship radar label"),
		FString(SkyguardCpgShipSystemLabel(ESkyguardPatrolShipSystem::Radar)),
		FString(TEXT("RADAR")));
	TestEqual(
		TEXT("ship launcher label"),
		FString(SkyguardCpgShipSystemLabel(ESkyguardPatrolShipSystem::Launcher)),
		FString(TEXT("LNCH")));
	TestTrue(TEXT("cannon tape includes flare count"), Cannon.ThreatLine.Contains(TEXT("FLR  6")));
	TestEqual(TEXT("snapshot flare count"), Cannon.FlareCount, 6);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgHudCountsForwardThreatTest,
	"Skyguard52.Apache.CpgHudCountsForwardThreat",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgHudCountsForwardThreatTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardCpgHudThreatWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>(
		FVector::ZeroVector,
		FRotator::ZeroRotator);
	ASkyguardDrone* Armor = World->SpawnActor<ASkyguardDrone>(
		FVector(2000.f, 0.f, 0.f),
		FRotator::ZeroRotator);
	TestNotNull(TEXT("gunner"), Gunner);
	TestNotNull(TEXT("armor"), Armor);
	if (!Gunner || !Armor)
	{
		World->DestroyWorld(false);
		return false;
	}

	Armor->ConfigureThreat(ESkyguardThreatKind::GroundArmor);
	const FSkyguardCpgHudSnapshot Snap = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("forward armor is a contact"), Snap.ThreatCount >= 1);
	TestTrue(TEXT("threat tape names armor"), Snap.ThreatLine.Contains(TEXT("ARM")));
	TestTrue(TEXT("threat tape still includes flare count"), Snap.ThreatLine.Contains(TEXT("FLR")));
	TestFalse(TEXT("no inbound warning without a live inbound"), Snap.ThreatLine.Contains(TEXT("INB")));

	TArray<FSkyguardCpgContactMark> Marks;
	Gunner->CollectCpgContactMarks(Marks);
	TestTrue(TEXT("contact marks include the forward armor"), Marks.Num() >= 1);
	bool bFoundArmor = false;
	for (const FSkyguardCpgContactMark& Mark : Marks)
	{
		if (Mark.Label == TEXT("ARM"))
		{
			bFoundArmor = true;
			TestFalse(TEXT("unacquired contact is not locked"), Mark.bLocked);
		}
	}
	TestTrue(TEXT("armor mark is labeled ARM"), bFoundArmor);

	World->DestroyWorld(false);
	return true;
}

namespace SkyguardCpgHudTests
{
	bool TapeContainsBannedTerm(const FSkyguardCpgHudSnapshot& Snap)
	{
		const FString Tape =
			Snap.WeaponLine + TEXT(" ") +
			Snap.RangeLine + TEXT(" ") +
			Snap.ThreatLine + TEXT(" ") +
			Snap.EufdLine + TEXT(" ") +
			Snap.PilotConfirmLine;
		const FString Lower = Tape.ToLower();
		return Lower.Contains(TEXT("igla")) ||
			Lower.Contains(TEXT("yak")) ||
			Lower.Contains(TEXT("rifle"));
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgHudTapesFlareAndInboundTest,
	"Skyguard52.Apache.CpgHudTapesFlareAndInbound",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgHudTapesFlareAndInboundTest::RunTest(const FString& Parameters)
{
	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	TestEqual(
		TEXT("inbound label is short CPG"),
		FString(SkyguardCpgInboundLabel()),
		FString(TEXT("INB")));
	TestEqual(
		TEXT("flare tape is a number"),
		SkyguardCpgFlareTape(6),
		FString(TEXT("FLR  6")));

	const FSkyguardCpgHudSnapshot Clear = Gunner->BuildCpgHudSnapshot();
	TestEqual(TEXT("default flare count"), Clear.FlareCount, Gunner->GetFlareCount());
	TestEqual(TEXT("six flares on tape"), Clear.FlareCount, 6);
	TestFalse(TEXT("no inbound at rest"), Clear.bMissileInbound);
	TestTrue(TEXT("threat tape includes flare count"), Clear.ThreatLine.Contains(TEXT("FLR  6")));
	TestTrue(TEXT("eufd tape includes flare count"), Clear.EufdLine.Contains(TEXT("FLR  6")));
	TestFalse(TEXT("inbound warning absent when clear"), Clear.ThreatLine.Contains(TEXT("INB")));
	TestFalse(TEXT("eufd inbound absent when clear"), Clear.EufdLine.Contains(TEXT("INB")));
	TestFalse(
		TEXT("clear tape has no banned terms"),
		SkyguardCpgHudTests::TapeContainsBannedTerm(Clear));

	Gunner->NotifyMissileInbound();
	const FSkyguardCpgHudSnapshot Inbound = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("inbound live on snapshot"), Inbound.bMissileInbound);
	TestTrue(TEXT("threat tape warns inbound"), Inbound.ThreatLine.Contains(TEXT("INB")));
	TestTrue(TEXT("eufd tape warns inbound"), Inbound.EufdLine.Contains(TEXT("INB")));
	TestTrue(TEXT("inbound tape still shows flares"), Inbound.ThreatLine.Contains(TEXT("FLR  6")));
	TestTrue(TEXT("inbound eufd still shows flares"), Inbound.EufdLine.Contains(TEXT("FLR  6")));
	TestFalse(
		TEXT("inbound tape has no banned terms"),
		SkyguardCpgHudTests::TapeContainsBannedTerm(Inbound));

	Gunner->PopFlares();
	TestTrue(TEXT("flare kills the inbound"), Gunner->TryDefeatInboundWithFlares());
	const FSkyguardCpgHudSnapshot After = Gunner->BuildCpgHudSnapshot();
	TestFalse(TEXT("inbound cleared"), After.bMissileInbound);
	TestEqual(TEXT("one flare spent"), After.FlareCount, 5);
	TestTrue(TEXT("tape shows remaining flares"), After.ThreatLine.Contains(TEXT("FLR  5")));
	TestTrue(TEXT("eufd shows remaining flares"), After.EufdLine.Contains(TEXT("FLR  5")));
	TestFalse(TEXT("inbound warning gone from threat tape"), After.ThreatLine.Contains(TEXT("INB")));
	TestFalse(TEXT("inbound warning gone from eufd"), After.EufdLine.Contains(TEXT("INB")));
	TestFalse(
		TEXT("after-flare tape has no banned terms"),
		SkyguardCpgHudTests::TapeContainsBannedTerm(After));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgHudReadsPilotConfirmGetterTest,
	"Skyguard52.Apache.CpgHudReadsPilotConfirmGetter",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgHudReadsPilotConfirmGetterTest::RunTest(const FString& Parameters)
{
	const FString IniPath = FPaths::ProjectConfigDir() / TEXT("DefaultInput.ini");
	FString IniText;
	TestTrue(
		TEXT("DefaultInput.ini is readable"),
		FFileHelper::LoadFileToString(IniText, *IniPath));
	TestTrue(
		TEXT("PopFlares stays Key=X"),
		IniText.Contains(TEXT("ActionName=\"PopFlares\"")) &&
			IniText.Contains(TEXT("Key=X")));
	TestTrue(
		TEXT("no new HUD confirm action binding"),
		!IniText.Contains(TEXT("PilotConfirm")) &&
			!IniText.Contains(TEXT("CpgConfirm")));

	const UInputSettings* Settings = GetDefault<UInputSettings>();
	TestNotNull(TEXT("UInputSettings"), Settings);
	if (Settings)
	{
		TArray<FInputActionKeyMapping> FlareMaps;
		Settings->GetActionMappingByName(TEXT("PopFlares"), FlareMaps);
		bool bHasX = false;
		for (const FInputActionKeyMapping& Mapping : FlareMaps)
		{
			bHasX |= Mapping.Key == EKeys::X;
		}
		TestTrue(TEXT("runtime PopFlares includes Key X"), bHasX);
	}

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardCpgHudPilotConfirmWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardApacheAircraft* Apache =
		World->SpawnActor<ASkyguardApacheAircraft>(
			FVector(0.f, 0.f, 800.f),
			FRotator::ZeroRotator);
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>(
		FVector::ZeroVector,
		FRotator::ZeroRotator);
	TestNotNull(TEXT("apache"), Apache);
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Apache || !Gunner)
	{
		World->DestroyWorld(false);
		return false;
	}
	Apache->DispatchBeginPlay();

	TestEqual(
		TEXT("no confirm until a command changes"),
		Apache->GetPilotConfirmationsIssued(),
		0);
	TestTrue(
		TEXT("HUD confirm is empty before a change"),
		SkyguardCpgPilotConfirmLine(Apache).IsEmpty());

	FSkyguardCpgHudSnapshot Rest = Gunner->BuildCpgHudSnapshot();
	SkyguardCpgHudApplyPilotConfirm(Rest, World);
	TestTrue(TEXT("host snapshot is empty before a change"), Rest.PilotConfirmLine.IsEmpty());
	TestEqual(TEXT("host copies zero confirm count"), Rest.PilotConfirmationsIssued, 0);

	const int32 ConfirmsBefore = Apache->GetPilotConfirmationsIssued();
	Apache->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestEqual(
		TEXT("IssuePilotCommand confirms once"),
		Apache->GetPilotConfirmationsIssued(),
		ConfirmsBefore + 1);

	const FString ExpectedLeft =
		SkyguardPilotVoice::ConfirmLineForCommand(ESkyguardPilotCommand::OrbitLeft);
	const FString FirstRead = SkyguardCpgPilotConfirmLine(Apache);
	TestEqual(
		TEXT("HUD reads last confirm from Apache getters"),
		FirstRead,
		ExpectedLeft);
	TestTrue(TEXT("orbit-left confirm is visible"), FirstRead.Contains(TEXT("Coming left")));

	FSkyguardCpgHudSnapshot AfterChange = Gunner->BuildCpgHudSnapshot();
	SkyguardCpgHudApplyPilotConfirm(AfterChange, World);
	TestEqual(
		TEXT("host snapshot shows the confirm line"),
		AfterChange.PilotConfirmLine,
		ExpectedLeft);
	TestEqual(
		TEXT("host snapshot copies confirm count"),
		AfterChange.PilotConfirmationsIssued,
		Apache->GetPilotConfirmationsIssued());
	TestFalse(
		TEXT("confirm tape has no banned terms"),
		SkyguardCpgHudTests::TapeContainsBannedTerm(AfterChange));
	TestFalse(
		TEXT("confirm string is not Yak/Igla/rifle"),
		SkyguardCpgHudHasLegacyLiveWording(AfterChange.PilotConfirmLine));

	const int32 AfterFirstChange = Apache->GetPilotConfirmationsIssued();
	for (int32 Tick = 0; Tick < 5; ++Tick)
	{
		FSkyguardCpgHudSnapshot TickSnap = Gunner->BuildCpgHudSnapshot();
		SkyguardCpgHudApplyPilotConfirm(TickSnap, World);
		TestEqual(
			TEXT("HUD re-read does not change the confirm line"),
			TickSnap.PilotConfirmLine,
			ExpectedLeft);
		TestEqual(
			TEXT("HUD re-read does not increment Apache confirms"),
			Apache->GetPilotConfirmationsIssued(),
			AfterFirstChange);
		TestEqual(
			TEXT("host tick copy stays at the last confirm count"),
			TickSnap.PilotConfirmationsIssued,
			AfterFirstChange);
	}

	Apache->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestEqual(
		TEXT("repeat command does not re-confirm"),
		Apache->GetPilotConfirmationsIssued(),
		AfterFirstChange);
	TestEqual(
		TEXT("repeat command keeps the last HUD confirm"),
		SkyguardCpgPilotConfirmLine(Apache),
		ExpectedLeft);

	Apache->IssuePilotCommand(ESkyguardPilotCommand::Hold);
	const FString ExpectedHold =
		SkyguardPilotVoice::ConfirmLineForCommand(ESkyguardPilotCommand::Hold);
	FSkyguardCpgHudSnapshot AfterHold = Gunner->BuildCpgHudSnapshot();
	SkyguardCpgHudApplyPilotConfirm(AfterHold, World);
	TestEqual(
		TEXT("new command updates the HUD confirm"),
		AfterHold.PilotConfirmLine,
		ExpectedHold);
	TestEqual(
		TEXT("hold confirm increments once"),
		Apache->GetPilotConfirmationsIssued(),
		AfterFirstChange + 1);
	TestTrue(TEXT("hold confirm is visible"), AfterHold.PilotConfirmLine.Contains(TEXT("Holding")));

	SkyguardCpgHudApplyPilotConfirm(AfterHold, Apache);
	TestEqual(
		TEXT("apply is idempotent"),
		AfterHold.PilotConfirmLine,
		ExpectedHold);

	FSkyguardCpgHudSnapshot NullApache;
	SkyguardCpgHudApplyPilotConfirm(
		NullApache,
		static_cast<const ASkyguardApacheAircraft*>(nullptr));
	TestTrue(TEXT("null Apache yields an empty confirm"), NullApache.PilotConfirmLine.IsEmpty());
	TestEqual(TEXT("null Apache yields a zero confirm count"), NullApache.PilotConfirmationsIssued, 0);

	FSkyguardCpgHudSnapshot NullWorld;
	SkyguardCpgHudApplyPilotConfirm(
		NullWorld,
		static_cast<const UWorld*>(nullptr));
	TestTrue(TEXT("null world yields an empty confirm"), NullWorld.PilotConfirmLine.IsEmpty());
	TestEqual(TEXT("null world yields a zero confirm count"), NullWorld.PilotConfirmationsIssued, 0);

	World->DestroyWorld(false);
	return true;
}

#endif
