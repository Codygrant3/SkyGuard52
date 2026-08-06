#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "SkyguardPhase4LandscapePerformanceCaptureAttempt06.generated.h"

/**
 * Inert-by-default immutable Attempt06 profiler controller.
 *
 * It accepts only P4.5-M01-LANDSCAPE-VISIBLE-006. Warmup and measurement
 * execute in the same process, CSV begins only after a continuous 30-second
 * ready interval, and startup/load frames are excluded by construction.
 */
UCLASS()
class SKYGUARD52_API
USkyguardPhase4LandscapePerformanceCaptureAttempt06 final
	: public UTickableWorldSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;
	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;
	virtual bool IsTickable() const override;

private:
	bool IsWorldReady(FString& OutIssue) const;
	void BeginWarmup();
	void RequestMeasurementStart();
	void ConfirmMeasurementStart();
	void FailMeasurementStart(const FString& Issue);
	void RequestMeasurementStop();
	void FinishAfterCsvFlush();
	bool WriteReceipt(const FString& Gate, const FString& Issue) const;

	bool bRequested = false;
	bool bWarmupStarted = false;
	bool bMeasurementStartRequested = false;
	bool bMeasurementStarted = false;
	bool bStopRequested = false;
	bool bFinalized = false;
	FString ContractId;
	FString RunId;
	FString ExpectedMap;
	FString ReceiptPath;
	double WarmupSeconds = 0.0;
	double MeasuredSeconds = 0.0;
	double WarmupStartPlatformSeconds = 0.0;
	double MeasurementStartRequestPlatformSeconds = 0.0;
	double MeasurementStartPlatformSeconds = 0.0;
	double StopRequestPlatformSeconds = 0.0;
	FDateTime WarmupStartedAtUtc;
	FDateTime MeasurementStartRequestedAtUtc;
	FDateTime MeasurementStartedAtUtc;
};
