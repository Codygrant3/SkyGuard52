#pragma once

#include "CoreMinimal.h"
#include "Sound/SoundBase.h"
#include "SkyguardAudioTypes.generated.h"

class USoundAttenuation;
class USoundConcurrency;
class USoundSubmixBase;

UENUM(BlueprintType)
enum class ESkyguardAudioEvent : uint8
{
	RifleShot,
	RifleMechanical,
	IglaSeekerSearch,
	IglaLock,
	IglaLaunch,
	IglaImpact,
	DroneMotor,
	DroneFlyby,
	ExplosionSmall,
	ExplosionHeavy,
	DebrisImpact
};

UENUM(BlueprintType)
enum class ESkyguardListenerPerspective : uint8
{
	RearCockpit,
	Exterior
};

USTRUCT(BlueprintType)
struct FSkyguardAudioEventDefinition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	ESkyguardAudioEvent Event = ESkyguardAudioEvent::RifleShot;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundBase> Sound;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundAttenuation> Attenuation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundConcurrency> Concurrency;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TSoftObjectPtr<USoundSubmixBase> OutputSubmix;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="0.0"))
	float CooldownSeconds = 0.05f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="0.05"))
	float EstimatedDurationSeconds = 0.5f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="1", ClampMax="32"))
	int32 MaxConcurrent = 4;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="0", ClampMax="100"))
	int32 Priority = 50;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="0.0"))
	float Volume = 1.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="0.1", ClampMax="4.0"))
	float Pitch = 1.f;
};

USTRUCT(BlueprintType)
struct FSkyguardAudioTelemetry
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly)
	int32 RequestedEvents = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 PlayedEvents = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 RejectedByCooldown = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 RejectedByConcurrency = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 RejectedMissingAsset = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 PriorityEvictions = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 PeakActiveVoices = 0;
};
