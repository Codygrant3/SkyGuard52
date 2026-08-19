#pragma once

#include "CoreMinimal.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardThreatTypes.h"

struct FSkyguardCpgContactMark
{
	FVector WorldLocation = FVector::ZeroVector;
	float BoundsRadius = 0.f;
	FString Label;
	bool bLocked = false;
	bool bSeeking = false;
	float LockAlpha = 0.f;
};

/** Eye-space NDC: X right, Y up, 0 = glass center, ±1 at the vertical FOV edge. */
struct FSkyguardCpgSightEyeProject
{
	FVector2D Ndc = FVector2D::ZeroVector;
	float RadiusNdc = 0.f;
	bool bInFront = false;
};

struct FSkyguardCpgProjectedSightMark
{
	FSkyguardCpgSightEyeProject Project;
	FString Label;
	bool bLocked = false;
	bool bSeeking = false;
};

/** Readable CPG tapes. Names do not imply quality — review does. */
struct FSkyguardCpgHudSnapshot
{
	FString WeaponLine;
	FString RangeLine;
	FString ThreatLine;
	FString EufdLine;
	FString LockLine;
	FString SightLine;
	FString StationStatus;
	ESkyguardGuidedLockPhase LockPhase = ESkyguardGuidedLockPhase::Search;
	ESkyguardCpgSightMode SightMode = ESkyguardCpgSightMode::Helmet;
	float RangeMeters = -1.f;
	int32 ThreatCount = 0;
	float HeadingDegrees = 0.f;
	float LockProgress = 0.f;
	int32 FlareCount = 0;
	bool bMissileInbound = false;
	FVector EyeLocation = FVector::ZeroVector;
	FRotator EyeRotation = FRotator::ZeroRotator;
	float EyeFovDegrees = 85.f;
	float EyeAspectRatio = 16.f / 9.f;
	TArray<FSkyguardCpgContactMark> ContactMarks;
	TArray<FSkyguardCpgProjectedSightMark> SightMarks;
};

const TCHAR* SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon Weapon);
const TCHAR* SkyguardCpgThreatLabel(ESkyguardThreatKind Kind);
const TCHAR* SkyguardCpgShipSystemLabel(ESkyguardPatrolShipSystem System);
const TCHAR* SkyguardCpgLockPhaseLabel(ESkyguardGuidedLockPhase Phase);
const TCHAR* SkyguardCpgSightLabel(ESkyguardCpgSightMode Sight);
const TCHAR* SkyguardCpgInboundLabel();
FString SkyguardCpgFlareTape(int32 FlareCount);
bool SkyguardCpgHudHasLegacyLiveWording(const FString& Text);

inline bool SkyguardCpgProjectWorldToEye(
	const FVector& WorldLocation,
	const float BoundsRadius,
	const FVector& EyeLocation,
	const FRotator& EyeRotation,
	const float VerticalFovDegrees,
	const float AspectRatio,
	FSkyguardCpgSightEyeProject& OutProject)
{
	OutProject = FSkyguardCpgSightEyeProject();
	const float Fov = FMath::Clamp(VerticalFovDegrees, 1.f, 179.f);
	const float Aspect = FMath::Max(AspectRatio, 0.05f);
	const FTransform Eye(EyeRotation, EyeLocation);
	const FVector Local = Eye.InverseTransformPosition(WorldLocation);
	if (Local.X <= KINDA_SMALL_NUMBER)
	{
		return false;
	}
	const float TanHalfFov = FMath::Tan(FMath::DegreesToRadians(Fov * 0.5f));
	const float DepthScale = Local.X * TanHalfFov;
	if (DepthScale <= KINDA_SMALL_NUMBER)
	{
		return false;
	}
	OutProject.bInFront = true;
	OutProject.Ndc.X = Local.Y / (DepthScale * Aspect);
	OutProject.Ndc.Y = Local.Z / DepthScale;
	OutProject.RadiusNdc = FMath::Max(BoundsRadius, 0.f) / DepthScale;
	return true;
}

inline FVector2D SkyguardCpgEyeNdcToAbsolute(
	const FVector2D& Ndc,
	const FVector2D& AbsoluteMin,
	const FVector2D& AbsoluteMax)
{
	const FVector2D Size = AbsoluteMax - AbsoluteMin;
	return FVector2D(
		AbsoluteMin.X + (Ndc.X * 0.5f + 0.5f) * Size.X,
		AbsoluteMin.Y + (0.5f - Ndc.Y * 0.5f) * Size.Y);
}

inline float SkyguardCpgEyeRadiusToAbsolute(
	const float RadiusNdc,
	const FVector2D& AbsoluteMin,
	const FVector2D& AbsoluteMax)
{
	return FMath::Abs(RadiusNdc) * FMath::Abs(AbsoluteMax.Y - AbsoluteMin.Y);
}

inline FVector2D SkyguardCpgAbsoluteToLocal(
	const FVector2D& Absolute,
	const FVector2D& AbsoluteMin,
	const FVector2D& LocalSize,
	const FVector2D& AbsoluteMax)
{
	const FVector2D AbsSize = AbsoluteMax - AbsoluteMin;
	const float X = FMath::Abs(AbsSize.X) > KINDA_SMALL_NUMBER
		? (Absolute.X - AbsoluteMin.X) / AbsSize.X * LocalSize.X
		: 0.f;
	const float Y = FMath::Abs(AbsSize.Y) > KINDA_SMALL_NUMBER
		? (Absolute.Y - AbsoluteMin.Y) / AbsSize.Y * LocalSize.Y
		: 0.f;
	return FVector2D(X, Y);
}
