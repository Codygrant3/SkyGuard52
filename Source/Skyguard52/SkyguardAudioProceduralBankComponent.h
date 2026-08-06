#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkyguardAudioProceduralBankComponent.generated.h"

class USoundBase;
class USoundWaveProcedural;

UENUM(BlueprintType)
enum class ESkyguardProceduralAuditionCue : uint8
{
	RifleImpulse,
	IglaLockTone,
	IglaLaunchImpulse,
	ExplosionSmall,
	ExplosionHeavy,
	RadioBeep
};

/**
 * Project-owned deterministic signals for development mix-path auditions.
 *
 * These are not substitutes for final recordings. They make it possible to
 * verify routing, playback, cooldowns and packaged audio-device behavior
 * lawfully before licensed/source-recorded content arrives. Audition is
 * compile-time disabled in Shipping.
 */
UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardAudioProceduralBankComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	USkyguardAudioProceduralBankComponent();
	virtual void BeginPlay() override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio|Development")
	void BuildDevelopmentCues();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio|Development")
	bool AuditionCue(ESkyguardProceduralAuditionCue Cue);

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio|Development")
	USoundBase* GetCue(ESkyguardProceduralAuditionCue Cue) const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio|Development")
	int32 GetCueCount() const { return Waves.Num(); }

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio|Development")
	int32 GetTotalGeneratedBytes() const { return TotalGeneratedBytes; }

	uint32 GetCueChecksum(ESkyguardProceduralAuditionCue Cue) const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio|Development")
	bool IsAuditionAllowed() const;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Development")
	bool bEnableDevelopmentAudition = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Development", meta=(ClampMin="8000", ClampMax="48000"))
	int32 SampleRate = 48000;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Development", meta=(ClampMin="65536", ClampMax="2097152"))
	int32 GeneratedByteBudget = 1048576;

private:
	UPROPERTY(Transient)
	TArray<TObjectPtr<USoundWaveProcedural>> Waves;

	TArray<TArray<uint8>> PCMData;
	TArray<uint32> Checksums;
	int32 TotalGeneratedBytes = 0;

	void BuildCue(ESkyguardProceduralAuditionCue Cue, float DurationSeconds);
	TArray<uint8> GeneratePCM(ESkyguardProceduralAuditionCue Cue, float DurationSeconds) const;
	static int32 CueIndex(ESkyguardProceduralAuditionCue Cue);
};
