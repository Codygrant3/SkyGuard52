#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgDebrief.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardCpgDebriefLoadoutTests.cpp and
// SkyguardCpgDebriefCargoCaptureTests.cpp.
// Empty-input / fail-closed public API only. No Director / Gunner /
// PatrolShip spawn. Does not re-test live cargo percent or loadout keys.

namespace SkyguardCpgDebriefFailClosedTests
{
	bool ExpectNullCaptureDefaults(
		FAutomationTestBase& Test,
		const FSkyguardCpgDebriefSnapshot& Snap)
	{
		const bool bValid = Test.TestTrue(
			TEXT("null capture is valid"),
			Snap.bValid);
		const bool bWon = Test.TestFalse(
			TEXT("null capture is not a win"),
			Snap.bWon);
		const bool bTitle = Test.TestEqual(
			TEXT("empty title falls back to Sortie"),
			Snap.MissionTitle,
			FString(TEXT("Sortie")));
		const bool bNarrative = Test.TestTrue(
			TEXT("null capture has empty outcome narrative"),
			Snap.OutcomeNarrative.IsEmpty());
		const bool bScore = Test.TestEqual(
			TEXT("null capture score stays 0"),
			Snap.Score,
			0);
		const bool bMedal = Test.TestEqual(
			TEXT("null capture medal stays 0"),
			Snap.Medal,
			0);
		const bool bShots = Test.TestEqual(
			TEXT("null capture shots stay 0"),
			Snap.ShotsFired,
			0);
		const bool bHits = Test.TestEqual(
			TEXT("null capture hits stay 0"),
			Snap.Hits,
			0);
		const bool bCargo = Test.TestEqual(
			TEXT("null capture cargo stays 100"),
			Snap.CargoPercent,
			100);
		const bool bRadar = Test.TestFalse(
			TEXT("null capture radar is not dead"),
			Snap.bRadarDead);
		const bool bSystems = Test.TestEqual(
			TEXT("null capture destroyed systems stay empty"),
			Snap.DestroyedSystems.Num(),
			0);
		const bool bLoadout = Test.TestEqual(
			TEXT("null capture loadout stays Balanced"),
			Snap.SelectedLoadout,
			ESkyguardLoadout::Balanced);
		const bool bCannon = Test.TestEqual(
			TEXT("null capture 30 mm ammo stays 0"),
			Snap.CannonReady,
			0);
		const bool bRockets = Test.TestEqual(
			TEXT("null capture Hydra ammo stays 0"),
			Snap.RocketReady,
			0);
		const bool bGuided = Test.TestEqual(
			TEXT("null capture Hellfire ammo stays 0"),
			Snap.GuidedReady,
			0);
		return bValid && bWon && bTitle && bNarrative && bScore && bMedal &&
			bShots && bHits && bCargo && bRadar && bSystems && bLoadout &&
			bCannon && bRockets && bGuided;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCpgDebriefFailClosedTest,
	"Skyguard52.Presentation.Sortie.CpgDebriefFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCpgDebriefFailClosedTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCpgDebriefFailClosedTests;

	const FSkyguardCpgDebriefSnapshot Snap =
		SkyguardCaptureCpgDebrief(nullptr, nullptr, nullptr);
	if (!ExpectNullCaptureDefaults(*this, Snap))
	{
		return false;
	}

	TestFalse(
		TEXT("Hold the orbit. is not banned CPG copy"),
		SkyguardCpgCopyHasBannedTerm(TEXT("Hold the orbit.")));
	TestFalse(
		TEXT("30 mm / Hydra / Hellfire is not banned CPG copy"),
		SkyguardCpgCopyHasBannedTerm(TEXT("30 mm · Hydra · Hellfire")));
	TestFalse(
		TEXT("empty copy is not banned"),
		SkyguardCpgCopyHasBannedTerm(FString()));
	TestTrue(
		TEXT("igla is banned"),
		SkyguardCpgCopyHasBannedTerm(TEXT("igla")));
	TestTrue(
		TEXT("Igla is banned case-insensitively"),
		SkyguardCpgCopyHasBannedTerm(TEXT("Igla")));
	TestTrue(
		TEXT("yak is banned"),
		SkyguardCpgCopyHasBannedTerm(TEXT("yak")));
	TestTrue(
		TEXT("YAK is banned case-insensitively"),
		SkyguardCpgCopyHasBannedTerm(TEXT("YAK")));
	TestTrue(
		TEXT("rifle is banned"),
		SkyguardCpgCopyHasBannedTerm(TEXT("rifle")));
	TestTrue(
		TEXT("Rifle is banned case-insensitively"),
		SkyguardCpgCopyHasBannedTerm(TEXT("Rifle")));

	const FString Copy = SkyguardBuildCpgDebriefCopy(Snap);
	TestTrue(TEXT("empty capture copy names Sortie"), Copy.Contains(TEXT("Sortie")));
	TestTrue(TEXT("empty capture copy is FAIL"), Copy.Contains(TEXT("FAIL")));
	TestFalse(TEXT("empty capture copy is not WIN"), Copy.Contains(TEXT("WIN")));
	TestTrue(
		TEXT("empty DestroyedSystems prints none"),
		Copy.Contains(TEXT("none")));
	TestTrue(
		TEXT("empty capture copy lists 30 mm / Hydra / Hellfire"),
		Copy.Contains(TEXT("30 mm · Hydra · Hellfire")));
	TestFalse(
		TEXT("empty capture copy bans Igla/Yak/rifle"),
		SkyguardCpgCopyHasBannedTerm(Copy));
	return true;
}

#endif
