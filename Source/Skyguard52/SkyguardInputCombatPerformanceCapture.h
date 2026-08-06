#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "SkyguardInputCombatPerformanceCapture.generated.h"

/**
 * Inert-by-default observer for the packaged M01 input-combat performance gate.
 *
 * The subsystem never drives input or combat. It activates only when the
 * SkyguardCombatPerf command-line contract is present, records notifications
 * from accepted gameplay paths, owns the bounded measurement lifecycle, and
 * emits the untrusted runtime receipt consumed by the independent verifier.
 */
UCLASS()
class SKYGUARD52_API USkyguardInputCombatPerformanceCapture final
	: public UTickableWorldSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;
	virtual bool IsTickable() const override;

	/** Record an event reached exclusively through a bound player-input wrapper. */
	static void RecordPlayerEvent(const UObject* WorldContext, FName EventName);

	/** Record an accepted gameplay transition; this method never causes it. */
	static void RecordGameplayEvent(const UObject* WorldContext, FName EventName);

	static bool IsCaptureActive(const UObject* WorldContext);

private:
	struct FRecordedEvent
	{
		FName Name;
		double SecondsFromStart = 0.0;
	};

	struct FTraceWindowState
	{
		FString RegionName;
		FString EndBookmark;
		double StartedSeconds = 0.0;
		double EarliestEndSeconds = 0.0;
		double RequestedEndSeconds = TNumericLimits<double>::Max();
		double MaximumEndSeconds = 0.0;
		uint64 RegionId = 0;
		bool bActive = false;
	};

	static USkyguardInputCombatPerformanceCapture* Resolve(
		const UObject* WorldContext);

	void TryStartMeasurement();
	void RecordEvent(FName EventName, bool bFromPlayerInput);
	void UpdateTraceWindows(double SecondsFromStart);
	void BeginTraceWindow(
		FName WindowId,
		const TCHAR* RegionName,
		const TCHAR* BeginBookmark,
		const TCHAR* EndBookmark,
		double MinimumDuration,
		double MaximumDuration,
		double AutomaticEndDelay = TNumericLimits<double>::Max());
	void RequestTraceWindowEnd(FName WindowId, double DelaySeconds);
	void EndTraceWindow(FName WindowId);
	void EndAllTraceWindows();
	void CompleteMeasurement();
	bool WriteReceipt(
		const FString& State,
		const FString& Gate,
		const TArray<FString>& Issues) const;
	bool HasRequiredEventCounts(TArray<FString>& OutIssues) const;

	bool bCaptureRequested = false;
	bool bMeasurementStarted = false;
	bool bFinalized = false;
	bool bObservedPlayerInput = false;
	FString RunId;
	FString RunKind;
	FString ReceiptPath;
	FString ExpectedMap;
	double RequestedDurationSeconds = 0.0;
	double StartPlatformSeconds = 0.0;
	FDateTime StartedAtUtc;
	TArray<FRecordedEvent> Events;
	TMap<FName, FTraceWindowState> TraceWindows;
};
