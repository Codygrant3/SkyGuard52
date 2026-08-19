#pragma once

#include "CoreMinimal.h"

/**
 * Drop a held guided lock when the target leaves the lock cone or
 * exceeds lock range. Flare dumps stay on FSkyguardGuidedLockRules.
 */
struct SKYGUARD52_API FSkyguardGuidedLockBreak
{
	/**
	 * @param bHasLock True when a lock is currently held.
	 * @param SeekerLocation Seeker / sensor world position.
	 * @param SeekerForward Seeker aim direction (need not be unit).
	 * @param TargetLocation Locked target world position.
	 * @param ConeDegrees Half-angle lock cone in degrees.
	 * @param MaxRange Maximum lock range in centimeters.
	 * @return True if the held lock should drop for cone or range.
	 */
	static bool ShouldDropLock(
		bool bHasLock,
		const FVector& SeekerLocation,
		const FVector& SeekerForward,
		const FVector& TargetLocation,
		float ConeDegrees,
		float MaxRange);
};
