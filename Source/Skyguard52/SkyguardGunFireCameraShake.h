#pragma once

#include "CoreMinimal.h"
#include "Shakes/LegacyCameraShake.h"
#include "SkyguardGunFireCameraShake.generated.h"

/** Short muzzle recoil shake scaled by gunner AppliedCameraShakeScale. */
UCLASS()
class SKYGUARD52_API USkyguardGunFireCameraShake : public ULegacyCameraShake
{
	GENERATED_BODY()

public:
	USkyguardGunFireCameraShake();
};