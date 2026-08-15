#pragma once

#include "CoreMinimal.h"
#include "SkyguardGunshipTypes.generated.h"

/**
 * Live Apache CPG station feel. Weapons are decisions: each station has a
 * job and a cost. Igla is not a player weapon; guided-missile fields may
 * still use Igla* names for the existing seeker/physics path.
 */
namespace SkyguardApacheCpgFeel
{
	/** Helmet-sight spam for near/soft targets. Cheap, visible recoil. */
	constexpr float CannonFireRate = 12.0f;
	constexpr float CannonDamage = 22.0f;
	constexpr float CannonRecoilPitch = 0.92f;
	constexpr float CannonTraceRange = 32000.f;
	constexpr int32 CannonMagazineSize = 30;
	constexpr int32 CannonReserve = 300;
	constexpr float CannonReloadSeconds = 1.7f;

	/** Area / shoreline / boats. Commit a salvo, then wait. Not a sniper. */
	constexpr float RocketSalvoSeconds = 1.65f;
	constexpr float RocketDamage = 85.0f;
	constexpr int32 RocketsPerSalvo = 5;
	constexpr float RocketSpreadDegrees = 5.4f;
	constexpr float RocketSplashRadius = 420.f;
	constexpr int32 RocketMagazineSize = 14;
	constexpr int32 RocketReserve = 24;
	constexpr float RocketReloadSeconds = 2.3f;

	/** Expensive lock. Armor / boats / scouts only. Fast attackers are cannon food. */
	constexpr float GuidedLockSeconds = 1.80f;
	constexpr float GuidedLockConeDegrees = 6.0f;
	constexpr float GuidedMinRange = 350.f;
	constexpr float GuidedMaxRange = 18000.f;
	constexpr float GuidedDamage = 240.0f;
	constexpr int32 GuidedMagazineSize = 2;
	constexpr int32 GuidedReserve = 6;
	constexpr float GuidedReloadSeconds = 2.8f;
}

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

/** Harbor Breaker patrol-ship systems. Not a single health bar. */
UENUM(BlueprintType)
enum class ESkyguardPatrolShipSystem : uint8
{
	Radar UMETA(DisplayName = "Search Radar"),
	Cannon UMETA(DisplayName = "Cannon"),
	Launcher UMETA(DisplayName = "Launcher"),
	Engines UMETA(DisplayName = "Engines"),
	DroneDeck UMETA(DisplayName = "Drone Deck")
};

UENUM(BlueprintType)
enum class ESkyguardPilotLine : uint8
{
	RadarLit,
	CargoHit,
	CargoCritical,
	ShipRadarDown,
	ShipEnginesDown,
	ShipLauncherDown,
	ShipCannonDown,
	ShipDeckDown,
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
