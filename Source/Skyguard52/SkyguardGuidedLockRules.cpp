#include "SkyguardGuidedLockRules.h"

ESkyguardGuidedLockPhase FSkyguardGuidedLockRules::PhaseFromProgress(
	const float Progress,
	const bool bHasCandidate)
{
	if (!bHasCandidate)
	{
		return ESkyguardGuidedLockPhase::Search;
	}

	const float Clamped = FMath::Clamp(Progress, 0.f, 1.f);
	if (Clamped < DetectProgressEnd)
	{
		return ESkyguardGuidedLockPhase::Detect;
	}
	if (Clamped < 1.f)
	{
		return ESkyguardGuidedLockPhase::Track;
	}
	return ESkyguardGuidedLockPhase::Lock;
}

bool FSkyguardGuidedLockRules::CanFire(const ESkyguardGuidedLockPhase Phase)
{
	return Phase == ESkyguardGuidedLockPhase::Lock;
}

float FSkyguardGuidedLockRules::LockSeconds(const ESkyguardCpgSightMode Sight)
{
	switch (Sight)
	{
	case ESkyguardCpgSightMode::TargetingSensor:
		return SensorLockSeconds;
	case ESkyguardCpgSightMode::Helmet:
		return HelmetLockSeconds;
	}
	checkNoEntry();
	return HelmetLockSeconds;
}

float FSkyguardGuidedLockRules::AcquireDegrees(const ESkyguardCpgSightMode Sight)
{
	switch (Sight)
	{
	case ESkyguardCpgSightMode::TargetingSensor:
		return SensorAcquireDegrees;
	case ESkyguardCpgSightMode::Helmet:
		return HelmetAcquireDegrees;
	}
	checkNoEntry();
	return HelmetAcquireDegrees;
}

bool FSkyguardGuidedLockRules::IsInsideAcquireCone(
	const float AngleDegrees,
	const ESkyguardCpgSightMode Sight)
{
	return AngleDegrees <= AcquireDegrees(Sight);
}

ESkyguardGuidedLockPhase FSkyguardGuidedLockRules::StepLock(
	float& Progress,
	bool& bHasCandidate,
	const float DeltaSeconds,
	const ESkyguardCpgSightMode Sight,
	const float AngleDegrees,
	const bool bFlarePopped)
{
	if (bFlarePopped)
	{
		Progress = 0.f;
		bHasCandidate = false;
		return PhaseFromProgress(Progress, bHasCandidate);
	}

	if (bHasCandidate && IsInsideAcquireCone(AngleDegrees, Sight))
	{
		Progress = FMath::Clamp(
			Progress + DeltaSeconds / FMath::Max(LockSeconds(Sight), 0.1f),
			0.f,
			1.f);
	}

	return PhaseFromProgress(Progress, bHasCandidate);
}

const TCHAR* FSkyguardGuidedLockRules::PhaseLabel(
	const ESkyguardGuidedLockPhase Phase)
{
	switch (Phase)
	{
	case ESkyguardGuidedLockPhase::Search:
		return TEXT("SRCH");
	case ESkyguardGuidedLockPhase::Detect:
		return TEXT("DET");
	case ESkyguardGuidedLockPhase::Track:
		return TEXT("TRK");
	case ESkyguardGuidedLockPhase::Lock:
		return TEXT("LCK");
	}
	checkNoEntry();
	return TEXT("SRCH");
}

const TCHAR* FSkyguardGuidedLockRules::SightLabel(
	const ESkyguardCpgSightMode Sight)
{
	switch (Sight)
	{
	case ESkyguardCpgSightMode::TargetingSensor:
		return TEXT("SNSR");
	case ESkyguardCpgSightMode::Helmet:
		return TEXT("HMD");
	}
	checkNoEntry();
	return TEXT("HMD");
}
