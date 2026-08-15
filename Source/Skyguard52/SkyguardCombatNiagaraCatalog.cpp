#include "SkyguardCombatNiagaraCatalog.h"

#include "NiagaraSystem.h"
#include "UObject/StrongObjectPtr.h"

namespace
{
	UNiagaraSystem* ResolveOnce(
		const FSoftObjectPath& Path,
		bool& bAttempted,
		TStrongObjectPtr<UNiagaraSystem>& CachedSystem)
	{
		if (!bAttempted)
		{
			bAttempted = true;
			CachedSystem.Reset(Cast<UNiagaraSystem>(Path.TryLoad()));
		}
		return CachedSystem.Get();
	}
}

FSoftObjectPath USkyguardCombatNiagaraCatalog::GetMuzzleFlashPath()
{
	return FSoftObjectPath(
		TEXT("/Game/Skyguard/VFX/NS_MuzzleFlash.NS_MuzzleFlash"));
}

FSoftObjectPath USkyguardCombatNiagaraCatalog::GetGunSmokePath()
{
	return FSoftObjectPath(
		TEXT("/Game/Skyguard/VFX/NS_GunSmoke.NS_GunSmoke"));
}

FSoftObjectPath USkyguardCombatNiagaraCatalog::GetHitSparksPath()
{
	return FSoftObjectPath(
		TEXT("/Game/Skyguard/VFX/NS_HitSparks.NS_HitSparks"));
}

FSoftObjectPath USkyguardCombatNiagaraCatalog::GetDroneExplosionPath()
{
	return FSoftObjectPath(
		TEXT("/Game/Skyguard/VFX/NS_DroneExplosion.NS_DroneExplosion"));
}

FSoftObjectPath USkyguardCombatNiagaraCatalog::GetMissileTrailPath()
{
	return FSoftObjectPath(
		TEXT("/Game/Skyguard/VFX/NS_MissileTrail.NS_MissileTrail"));
}

FSoftObjectPath USkyguardCombatNiagaraCatalog::GetIglaLaunchPath()
{
	return FSoftObjectPath(
		TEXT("/Game/Skyguard/VFX/NS_IglaLaunch.NS_IglaLaunch"));
}

UNiagaraSystem* USkyguardCombatNiagaraCatalog::ResolveMuzzleFlash()
{
	static bool bAttempted = false;
	static TStrongObjectPtr<UNiagaraSystem> CachedSystem;
	return ResolveOnce(GetMuzzleFlashPath(), bAttempted, CachedSystem);
}

UNiagaraSystem* USkyguardCombatNiagaraCatalog::ResolveGunSmoke()
{
	static bool bAttempted = false;
	static TStrongObjectPtr<UNiagaraSystem> CachedSystem;
	return ResolveOnce(GetGunSmokePath(), bAttempted, CachedSystem);
}

UNiagaraSystem* USkyguardCombatNiagaraCatalog::ResolveHitSparks()
{
	static bool bAttempted = false;
	static TStrongObjectPtr<UNiagaraSystem> CachedSystem;
	return ResolveOnce(GetHitSparksPath(), bAttempted, CachedSystem);
}

UNiagaraSystem* USkyguardCombatNiagaraCatalog::ResolveDroneExplosion()
{
	static bool bAttempted = false;
	static TStrongObjectPtr<UNiagaraSystem> CachedSystem;
	return ResolveOnce(GetDroneExplosionPath(), bAttempted, CachedSystem);
}

UNiagaraSystem* USkyguardCombatNiagaraCatalog::ResolveMissileTrail()
{
	static bool bAttempted = false;
	static TStrongObjectPtr<UNiagaraSystem> CachedSystem;
	return ResolveOnce(GetMissileTrailPath(), bAttempted, CachedSystem);
}

UNiagaraSystem* USkyguardCombatNiagaraCatalog::ResolveIglaLaunch()
{
	static bool bAttempted = false;
	static TStrongObjectPtr<UNiagaraSystem> CachedSystem;
	return ResolveOnce(GetIglaLaunchPath(), bAttempted, CachedSystem);
}
