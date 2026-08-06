#include "SkyguardCombatVFX.h"
#include "Engine/World.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInterface.h"

UStaticMesh* USkyguardCombatVFX::SphereMesh()
{
	static UStaticMesh* M = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	return M;
}
UStaticMesh* USkyguardCombatVFX::ConeMesh()
{
	static UStaticMesh* M = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cone.Cone"));
	return M;
}
UStaticMesh* USkyguardCombatVFX::CylinderMesh()
{
	static UStaticMesh* M = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	return M;
}
UMaterialInterface* USkyguardCombatVFX::LoadMat(const TCHAR* Path)
{
	return LoadObject<UMaterialInterface>(nullptr, Path);
}

void USkyguardCombatVFX::SpawnOne(UWorld* World, UStaticMesh* Mesh, const FVector& Loc, const FVector& Scale, const FRotator& Rot, UMaterialInterface* Mat, float Life)
{
	if (!World || !Mesh) return;
	FActorSpawnParameters Params;
	Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	AStaticMeshActor* A = World->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), Loc, Rot, Params);
	if (!A) return;
	if (USceneComponent* Root = A->GetRootComponent()) { Root->SetMobility(EComponentMobility::Movable); }
	if (UStaticMeshComponent* C = A->GetStaticMeshComponent())
	{
		C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		C->SetStaticMesh(Mesh);
		C->SetWorldScale3D(Scale);
		if (Mat)
		{
			C->SetMaterial(0, Mat);
		}
		C->SetCastShadow(false);
	}
	A->SetLifeSpan(FMath::Max(0.05f, Life));
}

void USkyguardCombatVFX::SpawnBurst(UWorld* World, const FVector& Loc, int32 Count, float Radius, float ScaleMin, float ScaleMax, UMaterialInterface* Mat, float Life, const FVector& Bias)
{
	UStaticMesh* Mesh = SphereMesh();
	if (!World || !Mesh) return;
	for (int32 i = 0; i < Count; ++i)
	{
		const FVector Offset = FMath::VRand() * FMath::FRandRange(0.f, Radius) + Bias;
		const float S = FMath::FRandRange(ScaleMin, ScaleMax);
		SpawnOne(World, Mesh, Loc + Offset, FVector(S), FRotator::ZeroRotator, Mat, Life * FMath::FRandRange(0.7f, 1.2f));
	}
}

void USkyguardCombatVFX::SpawnMuzzleFlash(UWorld* World, const FVector& Loc, const FVector& Dir)
{
	UMaterialInterface* Hot = LoadMat(TEXT("/Game/Skyguard/Materials/Generated/MI_MuzzleFlash_Hot.MI_MuzzleFlash_Hot"));
	if (!Hot) Hot = LoadMat(TEXT("/Game/Skyguard/Materials/M_ExhaustGlow.M_ExhaustGlow"));
	SpawnBurst(World, Loc, 10, 10.f, 0.04f, 0.12f, Hot, 0.07f, Dir.GetSafeNormal() * 8.f);
	// core flash
	SpawnOne(World, SphereMesh(), Loc + Dir.GetSafeNormal() * 6.f, FVector(0.18f, 0.18f, 0.18f), FRotator::ZeroRotator, Hot, 0.05f);
	// cone flash
	const FRotator ConeRot = Dir.Rotation() + FRotator(-90.f, 0.f, 0.f);
	SpawnOne(World, ConeMesh(), Loc + Dir.GetSafeNormal() * 14.f, FVector(0.12f, 0.12f, 0.35f), ConeRot, Hot, 0.06f);
}

void USkyguardCombatVFX::SpawnGunSmoke(UWorld* World, const FVector& Loc, const FVector& Dir)
{
	UMaterialInterface* Smoke = LoadMat(TEXT("/Game/Skyguard/Materials/M_Tex_L8_plaster2.M_Tex_L8_plaster2"));
	if (!Smoke) Smoke = LoadMat(TEXT("/Game/Skyguard/Materials/M_CityConcrete.M_CityConcrete"));
	SpawnBurst(World, Loc - Dir.GetSafeNormal() * 4.f, 6, 8.f, 0.08f, 0.2f, Smoke, 0.35f, FVector(0,0,4.f));
}

void USkyguardCombatVFX::SpawnHitSparks(UWorld* World, const FVector& Loc, const FVector& Normal)
{
	UMaterialInterface* Hot = LoadMat(TEXT("/Game/Skyguard/Materials/Generated/MI_MuzzleFlash_Hot.MI_MuzzleFlash_Hot"));
	if (!Hot) Hot = LoadMat(TEXT("/Game/Skyguard/Materials/M_ExhaustGlow.M_ExhaustGlow"));
	SpawnBurst(World, Loc, 12, 18.f, 0.03f, 0.09f, Hot, 0.12f, Normal.GetSafeNormal() * 10.f);
}

void USkyguardCombatVFX::SpawnExplosion(UWorld* World, const FVector& Loc, float Scale)
{
	UMaterialInterface* Core = LoadMat(TEXT("/Game/Skyguard/Materials/Generated/MI_ExplosionCore.MI_ExplosionCore"));
	if (!Core) Core = LoadMat(TEXT("/Game/Skyguard/Materials/M_ExhaustGlow.M_ExhaustGlow"));
	UMaterialInterface* Smoke = LoadMat(TEXT("/Game/Skyguard/Materials/M_Tex_L8_plaster2.M_Tex_L8_plaster2"));
	if (!Smoke) Smoke = LoadMat(TEXT("/Game/Skyguard/Materials/M_CityConcrete.M_CityConcrete"));
	UMaterialInterface* Flak = LoadMat(TEXT("/Game/Skyguard/Materials/Generated/MI_FlakFlash.MI_FlakFlash"));
	if (!Flak) Flak = Core;

	const float S = FMath::Clamp(Scale, 0.4f, 3.f);
	SpawnOne(World, SphereMesh(), Loc, FVector(1.2f * S), FRotator::ZeroRotator, Core, 0.18f);
	SpawnBurst(World, Loc, 16, 70.f * S, 0.25f * S, 0.8f * S, Core, 0.28f);
	SpawnBurst(World, Loc + FVector(0,0,30.f * S), 10, 90.f * S, 0.5f * S, 1.4f * S, Smoke, 0.9f);
	SpawnBurst(World, Loc, 8, 50.f * S, 0.2f * S, 0.5f * S, Flak, 0.2f);
}

void USkyguardCombatVFX::SpawnMissileTrail(UWorld* World, const FVector& Start, const FVector& End)
{
	UMaterialInterface* Trail = LoadMat(TEXT("/Game/Skyguard/Materials/Generated/MI_DroneTrail.MI_DroneTrail"));
	if (!Trail) Trail = LoadMat(TEXT("/Game/Skyguard/Materials/M_ExhaustGlow.M_ExhaustGlow"));
	const FVector Delta = End - Start;
	const float Dist = Delta.Size();
	const FVector Dir = Delta.GetSafeNormal();
	const int32 Beads = FMath::Clamp(FMath::RoundToInt(Dist / 120.f), 4, 28);
	for (int32 i = 0; i < Beads; ++i)
	{
		const float T = (i + 1) / float(Beads);
		const FVector P = Start + Dir * (Dist * T);
		const float S = FMath::Lerp(0.18f, 0.06f, T);
		SpawnOne(World, SphereMesh(), P, FVector(S), FRotator::ZeroRotator, Trail, 0.25f + (1.f - T) * 0.2f);
	}
}

void USkyguardCombatVFX::SpawnIglaLaunch(UWorld* World, const FVector& Loc, const FVector& Dir)
{
	UMaterialInterface* Hot = LoadMat(TEXT("/Game/Skyguard/Materials/Generated/MI_MuzzleFlash_Hot.MI_MuzzleFlash_Hot"));
	if (!Hot) Hot = LoadMat(TEXT("/Game/Skyguard/Materials/M_ExhaustGlow.M_ExhaustGlow"));
	UMaterialInterface* Smoke = LoadMat(TEXT("/Game/Skyguard/Materials/M_Tex_L8_plaster2.M_Tex_L8_plaster2"));
	SpawnBurst(World, Loc, 14, 16.f, 0.08f, 0.22f, Hot, 0.12f, Dir.GetSafeNormal() * 20.f);
	if (Smoke)
	{
		SpawnBurst(World, Loc - Dir.GetSafeNormal() * 20.f, 10, 22.f, 0.15f, 0.4f, Smoke, 0.55f, FVector(0,0,8.f));
	}
}

void USkyguardCombatVFX::SpawnTracer(UWorld* World, const FVector& Start, const FVector& End)
{
	UMaterialInterface* Hot = LoadMat(TEXT("/Game/Skyguard/Materials/Generated/MI_MuzzleFlash_Hot.MI_MuzzleFlash_Hot"));
	if (!Hot) Hot = LoadMat(TEXT("/Game/Skyguard/Materials/M_ExhaustGlow.M_ExhaustGlow"));
	const FVector Mid = (Start + End) * 0.5f;
	const FVector Delta = End - Start;
	const float Len = FMath::Clamp(Delta.Size() * 0.0008f, 0.4f, 8.f);
	const FRotator Rot = Delta.Rotation() + FRotator(0.f, 0.f, 90.f);
	SpawnOne(World, CylinderMesh(), Mid, FVector(0.04f, 0.04f, Len), Rot, Hot, 0.05f);
}
