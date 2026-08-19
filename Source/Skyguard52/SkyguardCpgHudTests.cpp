#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignRoster.h"
#include "SkyguardCpgHud.h"
#include "SkyguardDrone.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardThreatTypes.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

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
	TestFalse(
		TEXT("overlay hides inbound without a live inbound"),
		SkyguardCpgHudOverlayThreatTape(Snap).Contains(TEXT("INB")));
	TestTrue(
		TEXT("overlay still names the contact count"),
		SkyguardCpgHudOverlayThreatTape(Snap).Contains(TEXT("THRT")));

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
			Snap.EufdLine;
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

	FSkyguardCpgHudSnapshot Applied;
	Applied.FlareCount = 6;
	Applied.EufdLine = TEXT("30MM  RDY  HMD");
	SkyguardCpgHudApplyInboundTape(Applied);
	TestFalse(TEXT("apply is a no-op when inbound is down"), Applied.bMissileInbound);
	TestFalse(
		TEXT("apply does not invent inbound tape"),
		Applied.ThreatLine.Contains(TEXT("INB")));
	Applied.bMissileInbound = true;
	SkyguardCpgHudApplyInboundTape(Applied);
	TestTrue(TEXT("apply writes inbound on the threat tape"), Applied.ThreatLine.Contains(TEXT("INB")));
	TestTrue(TEXT("apply keeps flares on the threat tape"), Applied.ThreatLine.Contains(TEXT("FLR  6")));
	TestTrue(TEXT("apply writes inbound on the eufd tape"), Applied.EufdLine.Contains(TEXT("INB")));
	TestFalse(
		TEXT("applied inbound tape bans Igla/Yak/rifle"),
		SkyguardCpgHudHasLegacyLiveWording(Applied.ThreatLine + Applied.EufdLine));

	const FSkyguardCpgHudSnapshot Clear = Gunner->BuildCpgHudSnapshot();
	TestEqual(TEXT("default flare count"), Clear.FlareCount, Gunner->GetFlareCount());
	TestEqual(TEXT("six flares on tape"), Clear.FlareCount, 6);
	TestFalse(TEXT("no inbound at rest"), Clear.bMissileInbound);
	TestTrue(TEXT("threat tape includes flare count"), Clear.ThreatLine.Contains(TEXT("FLR  6")));
	TestTrue(TEXT("eufd tape includes flare count"), Clear.EufdLine.Contains(TEXT("FLR  6")));
	TestFalse(TEXT("inbound warning absent when clear"), Clear.ThreatLine.Contains(TEXT("INB")));
	TestFalse(TEXT("eufd inbound absent when clear"), Clear.EufdLine.Contains(TEXT("INB")));
	TestFalse(
		TEXT("overlay tape hides inbound when clear"),
		SkyguardCpgHudOverlayThreatTape(Clear).Contains(TEXT("INB")));
	TestFalse(
		TEXT("clear tape has no banned terms"),
		SkyguardCpgHudTests::TapeContainsBannedTerm(Clear));

	Gunner->NotifyMissileInbound();
	const FSkyguardCpgHudSnapshot Inbound = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("inbound live on snapshot"), Inbound.bMissileInbound);
	TestTrue(TEXT("threat tape warns inbound"), Inbound.ThreatLine.Contains(TEXT("INB")));
	TestTrue(TEXT("eufd tape warns inbound"), Inbound.EufdLine.Contains(TEXT("INB")));
	TestTrue(
		TEXT("overlay tape warns inbound when live"),
		SkyguardCpgHudOverlayThreatTape(Inbound).Contains(TEXT("INB")));
	TestEqual(
		TEXT("overlay inbound tape is the CPG warning"),
		SkyguardCpgHudOverlayThreatTape(Inbound),
		FString(SkyguardCpgInboundLabel()));
	TestTrue(TEXT("inbound tape still shows flares"), Inbound.ThreatLine.Contains(TEXT("FLR  6")));
	TestTrue(TEXT("inbound eufd still shows flares"), Inbound.EufdLine.Contains(TEXT("FLR  6")));
	TestFalse(
		TEXT("inbound tape has no banned terms"),
		SkyguardCpgHudTests::TapeContainsBannedTerm(Inbound));
	TestFalse(
		TEXT("overlay inbound tape has no banned terms"),
		SkyguardCpgHudHasLegacyLiveWording(SkyguardCpgHudOverlayThreatTape(Inbound)));

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
		TEXT("overlay inbound hidden after flare"),
		SkyguardCpgHudOverlayThreatTape(After).Contains(TEXT("INB")));
	TestFalse(
		TEXT("after-flare tape has no banned terms"),
		SkyguardCpgHudTests::TapeContainsBannedTerm(After));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgHudShowsHarborInboundWarningTest,
	"Skyguard52.Apache.CpgHudShowsHarborInboundWarning",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgHudShowsHarborInboundWarningTest::RunTest(const FString& Parameters)
{
	TestEqual(
		TEXT("HUD slice does not retune radar-live inbound"),
		static_cast<double>(
			ASkyguardGunshipSortieDirector::IncomingRadarLiveIntervalSeconds),
		40.0);
	TestEqual(
		TEXT("HUD slice does not retune radar-down inbound"),
		static_cast<double>(
			ASkyguardGunshipSortieDirector::IncomingRadarDownIntervalSeconds),
		80.0);
	TestEqual(
		TEXT("HUD slice does not retune contact wave"),
		ASkyguardGunshipSortieDirector::ContactWaveCount,
		2);
	TestEqual(
		TEXT("HUD slice does not retune shore wave"),
		ASkyguardGunshipSortieDirector::ShoreWaveCount,
		4);

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardCpgHudHarborInboundWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	TestNotNull(TEXT("director"), Director);
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Director || !Gunner)
	{
		World->DestroyWorld(false);
		return false;
	}

	Director->bAutoStart = false;
	Director->StartMissionIndex(1);

	const FSkyguardCpgHudSnapshot Approach = Gunner->BuildCpgHudSnapshot();
	TestFalse(TEXT("approach inbound is not live"), Approach.bMissileInbound);
	TestFalse(
		TEXT("approach threat tape hides inbound"),
		Approach.ThreatLine.Contains(TEXT("INB")));
	TestFalse(
		TEXT("approach eufd hides inbound"),
		Approach.EufdLine.Contains(TEXT("INB")));
	TestFalse(
		TEXT("approach overlay hides inbound"),
		SkyguardCpgHudOverlayThreatTape(Approach).Contains(TEXT("INB")));

	Director->Tick(SkyguardCampaignRoster::Get(1).BeatSeconds[0] - 0.2f);
	TestEqual(
		TEXT("first inbound window stays on approach"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Approach);
	TestFalse(
		TEXT("approach tick does not fire inbound"),
		Gunner->IsMissileInbound());

	Director->Tick(0.3f);
	TestEqual(
		TEXT("harbor contact is the first inbound beat"),
		Director->GetBeat(),
		ESkyguardSortieBeat::InitialContact);
	TestTrue(TEXT("harbor contact inbound is live"), Gunner->IsMissileInbound());

	const FSkyguardCpgHudSnapshot Inbound = Gunner->BuildCpgHudSnapshot();
	TestTrue(TEXT("snapshot sees director inbound"), Inbound.bMissileInbound);
	TestTrue(TEXT("threat tape shows harbor inbound"), Inbound.ThreatLine.Contains(TEXT("INB")));
	TestTrue(TEXT("eufd tape shows harbor inbound"), Inbound.EufdLine.Contains(TEXT("INB")));
	TestEqual(
		TEXT("overlay tape is the inbound warning"),
		SkyguardCpgHudOverlayThreatTape(Inbound),
		FString(SkyguardCpgInboundLabel()));
	TestFalse(
		TEXT("harbor inbound tape bans Igla/Yak/rifle"),
		SkyguardCpgHudTests::TapeContainsBannedTerm(Inbound));
	TestFalse(
		TEXT("harbor inbound overlay bans Igla/Yak/rifle"),
		SkyguardCpgHudHasLegacyLiveWording(SkyguardCpgHudOverlayThreatTape(Inbound)));

	World->DestroyWorld(false);
	return true;
}

#endif
