#pragma once

#include "CoreMinimal.h"
#include "SkyguardThreatTypes.generated.h"

/**
 * Live threat roster. Shahed-style fast attackers are one option, not the
 * whole campaign. Keep names generic so missions can remix freely.
 */
UENUM(BlueprintType)
enum class ESkyguardThreatKind : uint8
{
	FastAttacker UMETA(DisplayName = "Fast Attacker"),
	HeavyAttacker UMETA(DisplayName = "Heavy Attacker"),
	RotorScout UMETA(DisplayName = "Rotor Scout"),
	GroundArmor UMETA(DisplayName = "Ground Armor"),
	FastBoat UMETA(DisplayName = "Fast Boat")
};
