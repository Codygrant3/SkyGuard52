#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossTypes.generated.h"

UENUM(BlueprintType)
enum class ESkyguardBossWeapon : uint8
{
	Rifle UMETA(DisplayName = "Rifle"),
	Igla UMETA(DisplayName = "Igla")
};

UENUM(BlueprintType)
enum class ESkyguardBossPhase : uint8
{
	Approach,
	Disarm,
	LockWindow,
	Critical,
	Defeated
};

UENUM(BlueprintType)
enum class ESkyguardPilotCommand : uint8
{
	Pursuit,
	Break,
	OrbitLeft,
	OrbitRight,
	Extend
};

USTRUCT(BlueprintType)
struct FSkyguardBossTelemetry
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 RifleHits = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 IglaHits = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 WeakPointsDestroyed = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 PilotCommandsIssued = 0;
};
