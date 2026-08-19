#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGuidedLockBreak.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedLockBreakStaysInConeAndRangeTest,
	"Skyguard52.Apache.GuidedMissile.LockStaysInConeAndRange",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedLockBreakStaysInConeAndRangeTest::RunTest(
	const FString& Parameters)
{
	const bool bShouldDrop = FSkyguardGuidedLockBreak::ShouldDropLock(
		true,
		FVector::ZeroVector,
		FVector::ForwardVector,
		FVector(5000.f, 0.f, 0.f),
		6.f,
		18000.f);
	TestFalse(
		TEXT("in-cone in-range lock stays"),
		bShouldDrop);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedLockBreakDropsOutsideConeTest,
	"Skyguard52.Apache.GuidedMissile.LockDropsOutsideCone",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedLockBreakDropsOutsideConeTest::RunTest(
	const FString& Parameters)
{
	const bool bShouldDrop = FSkyguardGuidedLockBreak::ShouldDropLock(
		true,
		FVector::ZeroVector,
		FVector::ForwardVector,
		FVector(5000.f, 5000.f, 0.f),
		6.f,
		18000.f);
	TestTrue(
		TEXT("target leaving the lock cone drops the lock"),
		bShouldDrop);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGuidedLockBreakDropsBeyondRangeTest,
	"Skyguard52.Apache.GuidedMissile.LockDropsBeyondRange",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGuidedLockBreakDropsBeyondRangeTest::RunTest(
	const FString& Parameters)
{
	const bool bShouldDrop = FSkyguardGuidedLockBreak::ShouldDropLock(
		true,
		FVector::ZeroVector,
		FVector::ForwardVector,
		FVector(20000.f, 0.f, 0.f),
		6.f,
		18000.f);
	TestTrue(
		TEXT("target beyond lock range drops the lock"),
		bShouldDrop);
	return true;
}

#endif
