#pragma once

#include "CoreMinimal.h"
#include "SkyguardGunshipTypes.generated.h"

/** Live Apache CPG stations. Igla is not a player weapon. */
UENUM(BlueprintType)
enum class ESkyguardGunshipWeapon : uint8
{
	Cannon UMETA(DisplayName = "30mm Cannon"),
	Rockets UMETA(DisplayName = "Rocket Pods"),
	GuidedMissile UMETA(DisplayName = "Guided Missile")
};

UENUM(BlueprintType)
enum class ESkyguardLoadout : uint8
{
	Balanced UMETA(DisplayName = "Balanced"),
	AntiArmor UMETA(DisplayName = "Anti-Armor"),
	RocketHeavy UMETA(DisplayName = "Rocket Heavy"),
	Intercept UMETA(DisplayName = "Intercept")
};

UENUM(BlueprintType)
enum class ESkyguardClimaxKind : uint8
{
	PatrolShip,
	RivalHelo,
	ArmorColumn,
	MixedSwarm
};

UENUM(BlueprintType)
enum class ESkyguardPilotLine : uint8
{
	RadarLit,
	CargoHit,
	CargoCritical,
	ShipRadarDown,
	ShipEnginesDown,
	ShipDead,
	Inbound,
	FlaresGood,
	Choice,
	Extract,
	GoThermal,
	Win,
	Fail,
	LoadoutPrompt
};
