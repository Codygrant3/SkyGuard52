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

/** Readable escalation for the guided-missile station. Fire is last. */
UENUM(BlueprintType)
enum class ESkyguardGuidedLockPhase : uint8
{
	Search UMETA(DisplayName = "Search"),
	Detect UMETA(DisplayName = "Detect"),
	Track UMETA(DisplayName = "Track"),
	Lock UMETA(DisplayName = "Lock")
};

/** Helmet-sight for near threats; targeting-sensor for hunting. */
UENUM(BlueprintType)
enum class ESkyguardCpgSightMode : uint8
{
	Helmet UMETA(DisplayName = "Helmet Sight"),
	TargetingSensor UMETA(DisplayName = "Targeting Sensor")
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
