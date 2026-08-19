#pragma once

#include "CoreMinimal.h"
#include "SkyguardGunshipTypes.h"

/**
 * Paper lock contract for the Apache CPG guided-missile station.
 * Search → detect → track → lock → fire. Helmet and targeting-sensor
 * do not share a cone or a clock.
 */
struct SKYGUARD52_API FSkyguardGuidedLockRules
{
	static constexpr float HelmetLockSeconds = 2.40f;
	static constexpr float SensorLockSeconds = 1.35f;
	static constexpr float HelmetAcquireDegrees = 12.0f;
	static constexpr float SensorAcquireDegrees = 5.5f;
	static constexpr float DetectProgressEnd = 0.22f;

	static ESkyguardGuidedLockPhase PhaseFromProgress(
		float Progress,
		bool bHasCandidate);

	static bool CanFire(ESkyguardGuidedLockPhase Phase);

	static float LockSeconds(ESkyguardCpgSightMode Sight);
	static float AcquireDegrees(ESkyguardCpgSightMode Sight);
	static bool IsInsideAcquireCone(
		float AngleDegrees,
		ESkyguardCpgSightMode Sight);

	/**
	 * One Hellfire step the CPG and tests call.
	 * In-cone dwell acquires and then holds lock. PopFlares (Key=X,
	 * already shipped) dumps the solution immediately.
	 */
	static ESkyguardGuidedLockPhase StepLock(
		float& Progress,
		bool& bHasCandidate,
		float DeltaSeconds,
		ESkyguardCpgSightMode Sight,
		float AngleDegrees,
		bool bFlarePopped);

	static const TCHAR* PhaseLabel(ESkyguardGuidedLockPhase Phase);
	static const TCHAR* SightLabel(ESkyguardCpgSightMode Sight);
};
