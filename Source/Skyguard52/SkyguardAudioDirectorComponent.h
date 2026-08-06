#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkyguardAudioTypes.h"
#include "SkyguardAudioProductionBank.h"
#include "SkyguardAudioDirectorComponent.generated.h"

class UAudioComponent;
class USceneComponent;
class USoundBase;
class UWorld;
class USkyguardAudioProductionBank;

UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardAudioDirectorComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	USkyguardAudioDirectorComponent();
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio")
	void PrimeConfiguredAssets();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio")
	void ApplyProductionBank(USkyguardAudioProductionBank* Bank);

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio")
	FSkyguardProductionAudioAudit GetProductionBankAudit() const;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio")
	bool TriggerEvent(ESkyguardAudioEvent Event, const FVector& WorldLocation);

	/** Route gameplay audio through the mission's registered director. */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio", meta=(WorldContext="WorldContextObject"))
	static bool TriggerWorldEvent(
		UObject* WorldContextObject,
		ESkyguardAudioEvent Event,
		const FVector& WorldLocation);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio")
	void SetEngineState(float NormalizedRpm, float NormalizedLoad, float AirspeedKph, float OpenCanopyFraction);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio")
	void SetListenerPerspective(ESkyguardListenerPerspective NewPerspective);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio")
	void ApplyHearingSuppression(float Strength, float DurationSeconds);

	/** Public deterministic update used by automation and non-ticking simulations. */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio")
	void AdvanceAudioState(float DeltaSeconds);

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio")
	FSkyguardAudioTelemetry GetTelemetry() const { return Telemetry; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio")
	float GetSuppressionAmount() const { return SuppressionAmount; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio")
	int32 GetActiveVoiceCount() const { return ActiveVoices.Num(); }

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio")
	float GetIdleBlend() const { return IdleBlend; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio")
	float GetCruiseBlend() const { return CruiseBlend; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio")
	float GetPowerBlend() const { return PowerBlend; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio")
	float GetWindBlend() const { return WindBlend; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio|Production")
	int32 GetResolvedProductionLoopRouteCount() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio|Production")
	bool AreResolvedProductionLoopRoutesComplete() const;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Events")
	TArray<FSkyguardAudioEventDefinition> EventDefinitions;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Engine")
	TSoftObjectPtr<USoundBase> EngineIdleLoop;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Engine")
	TSoftObjectPtr<USoundBase> EngineCruiseLoop;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Engine")
	TSoftObjectPtr<USoundBase> EnginePowerLoop;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Engine")
	TSoftObjectPtr<USoundBase> PropellerLoop;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Engine")
	TSoftObjectPtr<USoundBase> OpenCockpitWindLoop;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Budget", meta=(ClampMin="1", ClampMax="64"))
	int32 GlobalVoiceLimit = 24;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Production")
	TObjectPtr<USkyguardAudioProductionBank> ProductionBank;

	/** Default governed bank. It is loaded asynchronously during briefing. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Production")
	TSoftObjectPtr<USkyguardAudioProductionBank> ProductionBankAsset;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Mix", meta=(ClampMin="0.0", ClampMax="1.0"))
	float CockpitExteriorAttenuation = 0.72f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Mix", meta=(ClampMin="100.0"))
	float CockpitLowPassHz = 7200.f;

private:
	struct FActiveVoice
	{
		ESkyguardAudioEvent Event = ESkyguardAudioEvent::RifleShot;
		int32 Priority = 0;
		float RemainingSeconds = 0.f;
		TWeakObjectPtr<UAudioComponent> Component;
	};

	struct FResolvedLoopRoute
	{
		ESkyguardProductionAudioCategory Category =
			ESkyguardProductionAudioCategory::EngineIdle;
		TSoftObjectPtr<USoundBase> Sound;
		TSoftObjectPtr<USoundAttenuation> Attenuation;
		TSoftObjectPtr<USoundConcurrency> Concurrency;
		TSoftObjectPtr<USoundSubmixBase> OutputSubmix;
	};

	TArray<FActiveVoice> ActiveVoices;
	TMap<ESkyguardAudioEvent, float> Cooldowns;
	TArray<TSharedPtr<struct FStreamableHandle>> PrimeHandles;
	TArray<FResolvedLoopRoute> ResolvedLoopRoutes;
	bool bProductionBankPrimeRequested = false;
	bool bCockpitSoundMixPushed = false;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UAudioComponent>> LoopComponents;

	FSkyguardAudioTelemetry Telemetry;
	ESkyguardListenerPerspective ListenerPerspective = ESkyguardListenerPerspective::RearCockpit;
	float SuppressionAmount = 0.f;
	float SuppressionRemainingSeconds = 0.f;
	float IdleBlend = 1.f;
	float CruiseBlend = 0.f;
	float PowerBlend = 0.f;
	float WindBlend = 0.f;
	float Rpm = 0.f;
	float Load = 0.f;
	float Airspeed = 0.f;
	float CanopyOpen = 1.f;

	const FSkyguardAudioEventDefinition* FindDefinition(ESkyguardAudioEvent Event) const;
	void OnProductionBankLoaded();
	void OnConfiguredAssetsLoaded();
	void RebuildResolvedLoopRoutes();
	void StopLoopComponents();
	void ApplyListenerSoundMix();
	void CreateResolvedLoopComponents();
	void UpdateLoopMix();
};
