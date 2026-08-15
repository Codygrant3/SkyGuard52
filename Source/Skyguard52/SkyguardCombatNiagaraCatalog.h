#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "SkyguardCombatNiagaraCatalog.generated.h"

class UNiagaraSystem;

/** Optional Niagara complements for the primary pooled mesh combat effects. */
UCLASS()
class SKYGUARD52_API USkyguardCombatNiagaraCatalog : public UObject
{
	GENERATED_BODY()

public:
	static FSoftObjectPath GetMuzzleFlashPath();
	static FSoftObjectPath GetGunSmokePath();
	static FSoftObjectPath GetHitSparksPath();
	static FSoftObjectPath GetDroneExplosionPath();
	static FSoftObjectPath GetMissileTrailPath();
	static FSoftObjectPath GetIglaLaunchPath();

	static UNiagaraSystem* ResolveMuzzleFlash();
	static UNiagaraSystem* ResolveGunSmoke();
	static UNiagaraSystem* ResolveHitSparks();
	static UNiagaraSystem* ResolveDroneExplosion();
	static UNiagaraSystem* ResolveMissileTrail();
	static UNiagaraSystem* ResolveIglaLaunch();
};
