#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkyguardAudioAcceptanceHarness.generated.h"

USTRUCT(BlueprintType)
struct FSkyguardAudibleAcceptanceReceipt
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly)
	FString BuildSha256;

	UPROPERTY(BlueprintReadOnly)
	FString EvidenceSha256;

	UPROPERTY(BlueprintReadOnly)
	int32 SampleCount = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 PeakActiveVoices = 0;

	UPROPERTY(BlueprintReadOnly)
	int32 TotalUnderruns = 0;

	UPROPERTY(BlueprintReadOnly)
	float MaximumAudioThreadMs = 0.f;

	UPROPERTY(BlueprintReadOnly)
	float MaximumTruePeakDbTP = -120.f;

	UPROPERTY(BlueprintReadOnly)
	bool bPackagedDevelopmentBuild = false;

	UPROPERTY(BlueprintReadOnly)
	bool bAudibleDeviceObserved = false;

	UPROPERTY(BlueprintReadOnly)
	bool bCalibratedMetering = false;

	UPROPERTY(BlueprintReadOnly)
	bool bProductionBankReady = false;

	UPROPERTY(BlueprintReadOnly)
	bool bAccepted = false;
};

UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardAudioAcceptanceHarness : public UActorComponent
{
	GENERATED_BODY()

public:
	USkyguardAudioAcceptanceHarness();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio|Acceptance")
	void BeginEvidenceRun(
		const FString& BuildSha256,
		const FString& EvidenceSha256,
		bool bPackagedDevelopmentBuild,
		bool bAudibleDeviceObserved,
		bool bCalibratedMetering,
		bool bProductionBankReady);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio|Acceptance")
	void RecordMeasuredSample(
		int32 ActiveVoices,
		int32 UnderrunCount,
		float AudioThreadMs,
		float TruePeakDbTP);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Audio|Acceptance")
	bool CompleteEvidenceRun();

	UFUNCTION(BlueprintPure, Category="Skyguard|Audio|Acceptance")
	const FSkyguardAudibleAcceptanceReceipt& GetReceipt() const { return Receipt; }

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Acceptance", meta=(ClampMin="60"))
	int32 MinimumMeasuredSamples = 600;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Acceptance", meta=(ClampMin="1"))
	int32 MaximumAllowedVoices = 48;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Acceptance", meta=(ClampMin="0.1"))
	float MaximumAudioThreadMs = 2.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Audio|Acceptance", meta=(ClampMax="0.0"))
	float MaximumTruePeakDbTP = -1.f;

private:
	FSkyguardAudibleAcceptanceReceipt Receipt;
	bool bRunActive = false;
	static bool IsSha256(const FString& Value);
};

