#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGunshipSortieDirector.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardGunshipSortieTests.cpp.
// Remaining empty-director NewObject public getters only, before
// StartMissionIndex / SetPendingLoadout. Existing
// SkyguardGunshipSortieTests.cpp already covers weather play,
// inbound cadence, beat waves.
// NewObject only. No world, no Gunner / Yak / Igla / rifle.
// Does not call StartMissionIndex, StartNextMission, ConfirmContinue,
// SetPendingLoadout, SpawnCoastalConvoy, or ResolveSortie.
// Does not assert Harbor IncomingRadarLiveIntervalSeconds /
// IncomingRadarDownIntervalSeconds.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGunshipSortieDirectorEmptyFailClosedTest,
	"Skyguard52.Campaign.SortieDirector.EmptyFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGunshipSortieDirectorEmptyFailClosedTest::RunTest(
	const FString& Parameters)
{
	ASkyguardGunshipSortieDirector* Director =
		NewObject<ASkyguardGunshipSortieDirector>(GetTransientPackage());
	TestNotNull(TEXT("NewObject empty sortie director constructs"), Director);
	if (!Director)
	{
		return false;
	}

	TestTrue(
		TEXT("Constructor enables PrimaryActorTick"),
		Director->PrimaryActorTick.bCanEverTick);
	TestTrue(
		TEXT("Constructor Tags contains Skyguard.GunshipSortie"),
		Director->ActorHasTag(TEXT("Skyguard.GunshipSortie")));

	TestEqual(
		TEXT("NewObject GetPendingLoadout is Balanced"),
		Director->GetPendingLoadout(),
		ESkyguardLoadout::Balanced);
	TestFalse(
		TEXT("NewObject IsAwaitingContinue is false"),
		Director->IsAwaitingContinue());

	TestNull(TEXT("NewObject GetCargoAsset is nullptr"), Director->GetCargoAsset());
	TestNull(TEXT("NewObject GetRadarNode is nullptr"), Director->GetRadarNode());
	TestNull(TEXT("NewObject GetPatrolShip is nullptr"), Director->GetPatrolShip());

	TestEqual(TEXT("NewObject GetLastScore is 0"), Director->GetLastScore(), 0);
	TestEqual(TEXT("NewObject GetLastMedal is 0"), Director->GetLastMedal(), 0);
	TestEqual(TEXT("NewObject GetMissionIndex is 0"), Director->GetMissionIndex(), 0);

	TestEqual(
		TEXT("NewObject GetBeat is Approach"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Approach);
	TestFalse(TEXT("NewObject IsSortieOver is false"), Director->IsSortieOver());

	return true;
}

#endif
