#pragma once

#include "CoreMinimal.h"

class AActor;
class ASkyguardApacheAircraft;
class ASkyguardGunner;
class ASkyguardYak52Aircraft;
class USceneComponent;
class UWorld;

/**
 * Live player platform query. Apache is preferred. Yak remains a fallback
 * so historical mission tests keep working.
 */
struct SKYGUARD52_API FSkyguardPlayerAircraft
{
	static ASkyguardApacheAircraft* FindApache(const UWorld* World);
	static ASkyguardYak52Aircraft* FindYak(const UWorld* World);
	static AActor* FindPlatform(UWorld* World);
	static USceneComponent* FindGunnerMount(UWorld* World);
	static ASkyguardApacheAircraft* EnsureApache(UWorld* World);
	static void AttachGunner(
		ASkyguardGunner* Gunner,
		ASkyguardYak52Aircraft* YakFallback);
	static void ApplyHullDamage(AActor* Platform, float Amount);
	static float GetHullDamageFraction(const AActor* Platform);
	static bool IsPlayerPlatform(const AActor* Actor);
};
