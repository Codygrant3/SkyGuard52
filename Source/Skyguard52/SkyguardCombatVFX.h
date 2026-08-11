#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "SkyguardCombatVFX.generated.h"

class UWorld;
class UStaticMesh;
class UMaterialInterface;
class USkyguardCombatVFXPoolSubsystem;

/**
 * Lightweight runtime combat VFX that does not depend on empty Niagara shells.
 * Public calls retain their original behavior while a fixed, world-lifetime
 * component pool supplies the transitional mesh effects without combat-path
 * package loads or actor spawning.
 */
UCLASS()
class SKYGUARD52_API USkyguardCombatVFX : public UObject
{
	GENERATED_BODY()
public:
	static void SpawnMuzzleFlash(UWorld* World, const FVector& Loc, const FVector& Dir);
	static void SpawnGunSmoke(UWorld* World, const FVector& Loc, const FVector& Dir);
	static void SpawnHitSparks(UWorld* World, const FVector& Loc, const FVector& Normal);
	static void SpawnExplosion(UWorld* World, const FVector& Loc, float Scale = 1.f);
	static void SpawnMissileTrail(UWorld* World, const FVector& Start, const FVector& End);
	static void SpawnIglaLaunch(UWorld* World, const FVector& Loc, const FVector& Dir);
	static void SpawnTracer(UWorld* World, const FVector& Start, const FVector& End);

private:
	static USkyguardCombatVFXPoolSubsystem* Pool(UWorld* World);
	static void SpawnBurst(UWorld* World, const FVector& Loc, int32 Count, float Radius, float ScaleMin, float ScaleMax, UMaterialInterface* Mat, float Life, const FVector& Bias = FVector::ZeroVector);
	static void SpawnOne(UWorld* World, UStaticMesh* Mesh, const FVector& Loc, const FVector& Scale, const FRotator& Rot, UMaterialInterface* Mat, float Life);
};
