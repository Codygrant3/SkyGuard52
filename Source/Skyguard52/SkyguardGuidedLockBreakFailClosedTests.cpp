#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGuidedLockBreak.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardGuidedLockBreakTests.cpp.
// Remaining ShouldDropLock fail-closed public API only. No UObject,
// no world spawn. Existing SkyguardGuidedLockBreakTests.cpp already
// covers in-cone stay, out-of-cone drop, and beyond-range drop with
// bHasLock=true.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedLockBreakNoLockFarOffAxisTest,
	"Skyguard52.Apache.GuidedMissile.NoLockFarOffAxisDoesNotDrop",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedLockBreakNoLockFarOffAxisTest::RunTest(
	const FString& Parameters)
{
	const bool bShouldDrop = FSkyguardGuidedLockBreak::ShouldDropLock(
		false,
		FVector::ZeroVector,
		FVector::ForwardVector,
		FVector(20000.f, 20000.f, 0.f),
		6.f,
		18000.f);
	TestFalse(
		TEXT("no held lock does not drop when the target is far off-axis beyond range"),
		bShouldDrop);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedLockBreakNoLockInConeTest,
	"Skyguard52.Apache.GuidedMissile.NoLockInConeDoesNotDrop",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedLockBreakNoLockInConeTest::RunTest(
	const FString& Parameters)
{
	const bool bShouldDrop = FSkyguardGuidedLockBreak::ShouldDropLock(
		false,
		FVector::ZeroVector,
		FVector::ForwardVector,
		FVector(5000.f, 0.f, 0.f),
		6.f,
		18000.f);
	TestFalse(
		TEXT("no held lock does not drop when the target is in cone and range"),
		bShouldDrop);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedLockBreakCoincidentSeekerKeepsLockTest,
	"Skyguard52.Apache.GuidedMissile.CoincidentSeekerKeepsLock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedLockBreakCoincidentSeekerKeepsLockTest::RunTest(
	const FString& Parameters)
{
	const bool bShouldDrop = FSkyguardGuidedLockBreak::ShouldDropLock(
		true,
		FVector::ZeroVector,
		FVector::ForwardVector,
		FVector::ZeroVector,
		6.f,
		18000.f);
	TestFalse(
		TEXT("coincident seeker and target keep the held lock"),
		bShouldDrop);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedLockBreakZeroMaxRangeDropsLockTest,
	"Skyguard52.Apache.GuidedMissile.ZeroMaxRangeDropsLock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedLockBreakZeroMaxRangeDropsLockTest::RunTest(
	const FString& Parameters)
{
	const bool bShouldDrop = FSkyguardGuidedLockBreak::ShouldDropLock(
		true,
		FVector::ZeroVector,
		FVector::ForwardVector,
		FVector(5000.f, 0.f, 0.f),
		6.f,
		0.f);
	TestTrue(
		TEXT("held lock drops when MaxRange is 0"),
		bShouldDrop);
	return true;
}

#endif
