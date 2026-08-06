#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "SkyguardPhase4LandscapePerformanceCapture.generated.h"

/**
 * Inert-by-default Phase 4 Landscape profiler controller.
 *
 * It is enabled only by the exact P4.5 attempt05 command-line contract. The
 * warmup and measured interval run in one process, and CSV capture begins only
 * after BeginPlay, the governed map, viewport, camera manager, D3D12 SM6, and a
 * continuous warmup interval have all been proven.
 */
UCLASS()
class SKYGUARD52_API USkyguardPhase4LandscapePerformanceCapture final
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
