#include "SkyguardCombatVFX.h"

#include "SkyguardCombatVFXPoolSubsystem.h"
#include "Engine/World.h"

USkyguardCombatVFXPoolSubsystem* USkyguardCombatVFX::Pool(UWorld* World)
{
	return World
		? World->GetSubsystem<USkyguardCombatVFXPoolSubsystem>()
		: nullptr;
}

void USkyguardCombatVFX::SpawnOne(
	UWorld* World,
	UStaticMesh* Mesh,
	const FVector& Loc,
	const FVector& Scale,
	const FRotator& Rot,
	UMaterialInterface* Mat,
	const float Life)
{
	if (USkyguardCombatVFXPoolSubsystem* VFXPool = Pool(World))
	{
		VFXPool->EmitMesh(Mesh, Loc, Scale, Rot, Mat, Life);
	}
}

void USkyguardCombatVFX::SpawnBurst(
	UWorld* World,
	const FVector& Loc,
	const int32 Count,
	const float Radius,
	const float ScaleMin,
	const float ScaleMax,
	UMaterialInterface* Mat,
	const float Life,
	const FVector& Bias)
{
	USkyguardCombatVFXPoolSubsystem* VFXPool = Pool(World);
	UStaticMesh* Mesh = VFXPool ? VFXPool->GetSphereMesh() : nullptr;
	if (!VFXPool || !Mesh)
	{
		return;
	}

	for (int32 Index = 0; Index < Count; ++Index)
	{
		const FVector Offset =
			FMath::VRand() * FMath::FRandRange(0.f, Radius) + Bias;
		const float UniformScale = FMath::FRandRange(ScaleMin, ScaleMax);
		VFXPool->EmitMesh(
			Mesh,
			Loc + Offset,
			FVector(UniformScale),
			FRotator::ZeroRotator,
			Mat,
			Life * FMath::FRandRange(0.7f, 1.2f));
	}
}

void USkyguardCombatVFX::SpawnMuzzleFlash(
	UWorld* World,
	const FVector& Loc,
	const FVector& Dir)
{
	USkyguardCombatVFXPoolSubsystem* VFXPool = Pool(World);
	if (!VFXPool)
	{
		return;
	}

	UMaterialInterface* Hot = VFXPool->GetHotMaterial();
	const FVector Forward = Dir.GetSafeNormal();
	SpawnBurst(
		World, Loc, 10, 10.f, 0.04f, 0.12f, Hot, 0.07f,
		Forward * 8.f);
	SpawnOne(
		World,
		VFXPool->GetSphereMesh(),
		Loc + Forward * 6.f,
		FVector(0.18f),
		FRotator::ZeroRotator,
		Hot,
		0.05f);
	const FRotator ConeRotation =
		Dir.Rotation() + FRotator(-90.f, 0.f, 0.f);
	SpawnOne(
		World,
		VFXPool->GetConeMesh(),
		Loc + Forward * 14.f,
		FVector(0.12f, 0.12f, 0.35f),
		ConeRotation,
		Hot,
		0.06f);
}

void USkyguardCombatVFX::SpawnGunSmoke(
	UWorld* World,
	const FVector& Loc,
	const FVector& Dir)
{
	USkyguardCombatVFXPoolSubsystem* VFXPool = Pool(World);
	if (!VFXPool)
	{
		return;
	}
	SpawnBurst(
		World,
		Loc - Dir.GetSafeNormal() * 4.f,
		6,
		8.f,
		0.08f,
		0.2f,
		VFXPool->GetSmokeMaterial(),
		0.35f,
		FVector(0.f, 0.f, 4.f));
}

void USkyguardCombatVFX::SpawnHitSparks(
	UWorld* World,
	const FVector& Loc,
	const FVector& Normal)
{
	USkyguardCombatVFXPoolSubsystem* VFXPool = Pool(World);
	if (!VFXPool)
	{
		return;
	}
	SpawnBurst(
		World,
		Loc,
		12,
		18.f,
		0.03f,
		0.09f,
		VFXPool->GetHotMaterial(),
		0.12f,
		Normal.GetSafeNormal() * 10.f);
}

void USkyguardCombatVFX::SpawnExplosion(
	UWorld* World,
	const FVector& Loc,
	const float Scale)
{
	USkyguardCombatVFXPoolSubsystem* VFXPool = Pool(World);
	if (!VFXPool)
	{
		return;
	}

	UMaterialInterface* Core = VFXPool->GetExplosionMaterial();
	UMaterialInterface* Smoke = VFXPool->GetSmokeMaterial();
	UMaterialInterface* Flak = VFXPool->GetFlakMaterial();
	const float ClampedScale = FMath::Clamp(Scale, 0.4f, 3.f);
	SpawnOne(
		World,
		VFXPool->GetSphereMesh(),
		Loc,
		FVector(1.2f * ClampedScale),
		FRotator::ZeroRotator,
		Core,
		0.18f);
	SpawnBurst(
		World, Loc, 16, 70.f * ClampedScale,
		0.25f * ClampedScale, 0.8f * ClampedScale, Core, 0.28f);
	SpawnBurst(
		World,
		Loc + FVector(0.f, 0.f, 30.f * ClampedScale),
		10,
		90.f * ClampedScale,
		0.5f * ClampedScale,
		1.4f * ClampedScale,
		Smoke,
		0.9f);
	SpawnBurst(
		World, Loc, 8, 50.f * ClampedScale,
		0.2f * ClampedScale, 0.5f * ClampedScale, Flak, 0.2f);
}

void USkyguardCombatVFX::SpawnMissileTrail(
	UWorld* World,
	const FVector& Start,
	const FVector& End)
{
	USkyguardCombatVFXPoolSubsystem* VFXPool = Pool(World);
	if (!VFXPool)
	{
		return;
	}

	UMaterialInterface* Trail = VFXPool->GetTrailMaterial();
	const FVector Delta = End - Start;
	const float Distance = Delta.Size();
	const FVector Direction = Delta.GetSafeNormal();
	const int32 Beads =
		FMath::Clamp(FMath::RoundToInt(Distance / 120.f), 4, 28);
	for (int32 Index = 0; Index < Beads; ++Index)
	{
		const float Alpha = (Index + 1) / static_cast<float>(Beads);
		const FVector Position = Start + Direction * (Distance * Alpha);
		const float BeadScale = FMath::Lerp(0.18f, 0.06f, Alpha);
		SpawnOne(
			World,
			VFXPool->GetSphereMesh(),
			Position,
			FVector(BeadScale),
			FRotator::ZeroRotator,
			Trail,
			0.25f + (1.f - Alpha) * 0.2f);
	}
}

void USkyguardCombatVFX::SpawnIglaLaunch(
	UWorld* World,
	const FVector& Loc,
	const FVector& Dir)
{
	USkyguardCombatVFXPoolSubsystem* VFXPool = Pool(World);
	if (!VFXPool)
	{
		return;
	}

	const FVector Forward = Dir.GetSafeNormal();
	SpawnBurst(
		World, Loc, 14, 16.f, 0.08f, 0.22f,
		VFXPool->GetHotMaterial(), 0.12f, Forward * 20.f);
	SpawnBurst(
		World,
		Loc - Forward * 20.f,
		10,
		22.f,
		0.15f,
		0.4f,
		VFXPool->GetSmokeMaterial(),
		0.55f,
		FVector(0.f, 0.f, 8.f));
}

void USkyguardCombatVFX::SpawnTracer(
	UWorld* World,
	const FVector& Start,
	const FVector& End)
{
	USkyguardCombatVFXPoolSubsystem* VFXPool = Pool(World);
	if (!VFXPool)
	{
		return;
	}

	const FVector Midpoint = (Start + End) * 0.5f;
	const FVector Delta = End - Start;
	const float Length = FMath::Clamp(Delta.Size() * 0.0008f, 0.4f, 8.f);
	const FRotator Rotation =
		Delta.Rotation() + FRotator(0.f, 0.f, 90.f);
	SpawnOne(
		World,
		VFXPool->GetCylinderMesh(),
		Midpoint,
		FVector(0.04f, 0.04f, Length),
		Rotation,
		VFXPool->GetHotMaterial(),
		0.05f);
}
