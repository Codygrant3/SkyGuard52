#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgHud.h"
#include "SkyguardDrone.h"
#include "SkyguardGunner.h"
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
	FSkyguardCpgContactMark ArmorMark;
	for (const FSkyguardCpgContactMark& Mark : Marks)
	{
		if (Mark.Label == TEXT("ARM"))
		{
			ArmorMark = Mark;
			break;
		}
	}
	TestTrue(TEXT("armor mark carries BoundsRadius"), ArmorMark.BoundsRadius > 0.f);

	const FSkyguardCpgHudSnapshot Projected = Gunner->BuildCpgHudSnapshot();
	TestTrue(
		TEXT("snapshot projects the forward armor onto the sight"),
		Projected.SightMarks.Num() >= 1);
	bool bProjectedArmor = false;
	for (const FSkyguardCpgProjectedSightMark& Sight : Projected.SightMarks)
	{
		if (Sight.Label != TEXT("ARM"))
		{
			continue;
		}
		bProjectedArmor = true;
		TestTrue(TEXT("snapshot armor is in front of the CPG eye"), Sight.Project.bInFront);
		TestTrue(
			TEXT("forward armor sits near glass center"),
			FMath::Abs(Sight.Project.Ndc.X) < 0.45f &&
				FMath::Abs(Sight.Project.Ndc.Y) < 0.45f);
		FSkyguardCpgSightEyeProject Recheck;
		TestTrue(
			TEXT("snapshot reuses the eye-projection helper"),
			SkyguardCpgProjectWorldToEye(
				ArmorMark.WorldLocation,
				ArmorMark.BoundsRadius,
				Projected.EyeLocation,
				Projected.EyeRotation,
				Projected.EyeFovDegrees,
				Projected.EyeAspectRatio,
				Recheck));
		TestEqual(
			TEXT("snapshot Ndc X matches the helper"),
			Sight.Project.Ndc.X,
			Recheck.Ndc.X);
		TestEqual(
			TEXT("snapshot Ndc Y matches the helper"),
			Sight.Project.Ndc.Y,
			Recheck.Ndc.Y);
	}
	TestTrue(TEXT("snapshot includes an ARM sight mark"), bProjectedArmor);

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
	FSkyguardCpgSightProjectsBoundsRadiusToGlassTest,
	"Skyguard52.Apache.CpgSight.ProjectsBoundsRadiusToGlass",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgSightProjectsBoundsRadiusToGlassTest::RunTest(const FString& Parameters)
{
	const FVector EyeLocation = FVector::ZeroVector;
	const FRotator EyeRotation = FRotator::ZeroRotator;
	const float Fov = 90.f;
	const float Aspect = 1.f;
	const FVector2D AbsMin(100.f, 50.f);
	const FVector2D AbsMax(2020.f, 1130.f);
	const FVector2D LocalSize(1920.f, 1080.f);

	FSkyguardCpgSightEyeProject Ahead;
	TestTrue(
		TEXT("a point on the eye axis is in front"),
		SkyguardCpgProjectWorldToEye(
			FVector(1000.f, 0.f, 0.f),
			100.f,
			EyeLocation,
			EyeRotation,
			Fov,
			Aspect,
			Ahead));
	TestTrue(TEXT("ahead mark is in front"), Ahead.bInFront);
	TestEqual(TEXT("ahead Ndc X is glass center"), Ahead.Ndc.X, 0.f);
	TestEqual(TEXT("ahead Ndc Y is glass center"), Ahead.Ndc.Y, 0.f);
	TestEqual(TEXT("BoundsRadius 100 at 1000cm and 90fov is 0.1 Ndc"), Ahead.RadiusNdc, 0.1f);

	FSkyguardCpgSightEyeProject Right;
	TestTrue(
		TEXT("a point to the right of the eye projects"),
		SkyguardCpgProjectWorldToEye(
			FVector(1000.f, 200.f, 0.f),
			50.f,
			EyeLocation,
			EyeRotation,
			Fov,
			Aspect,
			Right));
	TestTrue(TEXT("right mark is in front"), Right.bInFront);
	TestEqual(TEXT("right mark Ndc X is +0.2"), Right.Ndc.X, 0.2f);
	TestEqual(TEXT("right mark Ndc Y stays centered"), Right.Ndc.Y, 0.f);
	TestTrue(TEXT("smaller BoundsRadius is a smaller glass mark"), Right.RadiusNdc < Ahead.RadiusNdc);

	FSkyguardCpgSightEyeProject Up;
	TestTrue(
		TEXT("a point above the eye projects"),
		SkyguardCpgProjectWorldToEye(
			FVector(1000.f, 0.f, 200.f),
			50.f,
			EyeLocation,
			EyeRotation,
			Fov,
			Aspect,
			Up));
	TestEqual(TEXT("up mark Ndc Y is +0.2"), Up.Ndc.Y, 0.2f);

	FSkyguardCpgSightEyeProject Behind;
	TestFalse(
		TEXT("a point behind the eye is rejected"),
		SkyguardCpgProjectWorldToEye(
			FVector(-400.f, 0.f, 0.f),
			80.f,
			EyeLocation,
			EyeRotation,
			Fov,
			Aspect,
			Behind));
	TestFalse(TEXT("behind mark is not in front"), Behind.bInFront);

	const FVector2D CenterAbs = SkyguardCpgEyeNdcToAbsolute(Ahead.Ndc, AbsMin, AbsMax);
	TestEqual(TEXT("center Ndc maps to glass absolute center X"), CenterAbs.X, 1060.f);
	TestEqual(TEXT("center Ndc maps to glass absolute center Y"), CenterAbs.Y, 590.f);

	const FVector2D CenterLocal = SkyguardCpgAbsoluteToLocal(
		CenterAbs,
		AbsMin,
		LocalSize,
		AbsMax);
	TestEqual(TEXT("AbsoluteToLocal puts the mark on glass center X"), CenterLocal.X, 960.f);
	TestEqual(TEXT("AbsoluteToLocal puts the mark on glass center Y"), CenterLocal.Y, 540.f);

	const float AbsRadius = SkyguardCpgEyeRadiusToAbsolute(Ahead.RadiusNdc, AbsMin, AbsMax);
	TestEqual(TEXT("0.1 Ndc radius is 108 absolute px on 1080 glass"), AbsRadius, 108.f);
	const FVector2D EdgeLocal = SkyguardCpgAbsoluteToLocal(
		CenterAbs + FVector2D(AbsRadius, 0.f),
		AbsMin,
		LocalSize,
		AbsMax);
	TestEqual(
		TEXT("AbsoluteToLocal preserves BoundsRadius size on the glass"),
		FVector2D::Distance(CenterLocal, EdgeLocal),
		108.f);

	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}
	const FSkyguardCpgHudSnapshot Snap = Gunner->BuildCpgHudSnapshot();
	TestEqual(
		TEXT("snapshot eye FOV matches the CPG getter"),
		Snap.EyeFovDegrees,
		Gunner->GetCpgEyeFovDegrees());
	TestEqual(
		TEXT("snapshot eye aspect matches the CPG getter"),
		Snap.EyeAspectRatio,
		Gunner->GetCpgEyeAspectRatio());
	TestTrue(TEXT("CPG eye FOV is a real sight FOV"), Snap.EyeFovDegrees > 1.f);
	TestTrue(TEXT("CPG eye aspect is positive"), Snap.EyeAspectRatio > 0.05f);
	return true;
}

#endif
