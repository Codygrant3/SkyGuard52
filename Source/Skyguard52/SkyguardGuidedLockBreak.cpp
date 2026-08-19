#include "SkyguardGuidedLockBreak.h"

bool FSkyguardGuidedLockBreak::ShouldDropLock(
	const bool bHasLock,
	const FVector& SeekerLocation,
	const FVector& SeekerForward,
	const FVector& TargetLocation,
	const float ConeDegrees,
	const float MaxRange)
{
	if (!bHasLock)
	{
		return false;
	}

	const FVector Offset = TargetLocation - SeekerLocation;
	const float Distance = Offset.Size();
	if (Distance > MaxRange)
	{
		return true;
	}

	if (Distance <= KINDA_SMALL_NUMBER)
	{
		return false;
	}

	const FVector Aim = SeekerForward.GetSafeNormal();
	const float CosAngle = FMath::Clamp(
		FVector::DotProduct(Aim, Offset / Distance),
		-1.f,
		1.f);
	const float AngleDegrees = FMath::RadiansToDegrees(FMath::Acos(CosAngle));
	return AngleDegrees > ConeDegrees;
}
