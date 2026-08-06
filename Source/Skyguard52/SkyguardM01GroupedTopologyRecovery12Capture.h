#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "SkyguardM01GroupedTopologyRecovery12Capture.generated.h"

class ACameraActor;

/**
 * Inert-by-default Recovery12 native high-resolution viewport capture.
 *
 * The live offscreen game viewport only needs to exist and render. Each
 * governed export uses UE's high-resolution screenshot dummy viewport at an
 * exact 2048x2048, so desktop/window constraints cannot silently reduce the
 * evidence dimensions.
 */
UCLASS()
class SKYGUARD52_API USkyguardM01GroupedTopologyRecovery12Capture final
	: public UTickableWorldSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;
	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;
	virtual bool IsTickable() const override;

	struct FCaptureRecord
	{
		FString Family;
		FString View;
		FString Path;
		FString CompletionMethod;
		int32 Width = 0;
		int32 Height = 0;
		double ActivePixelFraction = 0.0;
		double ActiveClippedFraction = 1.0;
		double ActiveP05 = 0.0;
		double ActiveP50 = 0.0;
		double ActiveP95 = 0.0;
		double ActiveDynamicRange = 0.0;
		int32 MaximumChannel = 0;
		int32 UniqueColorCount = 0;
		bool bLivenessPassed = false;
		bool bHardBoundsPassed = false;
	};

private:
	enum class EPhase : uint8
	{
		WaitForWorld,
		Warmup,
		PilotSettle,
		PilotAwaitScreenshot,
		ViewSettle,
		ViewAwaitScreenshot,
		Finished,
		Failed
	};

	bool IsWorldRenderable(FString& OutIssue) const;
	bool ConfigureScene();
	bool ConfigureView(const FString& Family, const FString& View);
	void RequestCurrentScreenshot(bool bPilot);
	void HandleScreenshotCaptured(
		int32 Width,
		int32 Height,
		const TArray<FColor>& Colors);
	bool TryCompleteCurrentCaptureFromFilesystem();
	void CompleteCurrentCapture(
		int32 Width,
		int32 Height,
		TArrayView64<const FColor> Colors,
		const FString& CompletionMethod,
		bool bPersistPng);
	FCaptureRecord BuildRecord(
		int32 Width,
		int32 Height,
		TArrayView64<const FColor> Colors) const;
	bool WritePng(
		const FString& Path,
		int32 Width,
		int32 Height,
		TArrayView64<const FColor> Colors) const;
	void RestoreScreenshotDelegateCVar();
	bool WriteReceipt(const FString& Gate, const FString& Issue) const;
	void MaybeLogDiagnostic(const FString& Issue);
	FIntPoint GetLiveViewportSize() const;
	FString PhaseName() const;
	void Fail(const FString& Issue);
	void Finish();
	void RestoreVisibility();

	bool bRequested = false;
	bool bSceneConfigured = false;
	bool bScreenshotPending = false;
	bool bCurrentRequestPilot = false;
	FString ContractId;
	FString ExpectedMap;
	FString OutputRoot;
	FString PendingPath;
	FString PendingFamily;
	FString PendingView;
	FString LastReadinessIssue;
	FString InitializationFailure;
	EPhase Phase = EPhase::WaitForWorld;
	int32 ConsecutiveReadyFrames = 0;
	int32 WarmupFrames = 0;
	int32 SettleFrames = 0;
	int32 PilotIndex = 0;
	int32 ViewIndex = 0;
	int32 PendingFileStableFrames = 0;
	int64 PendingObservedFileSize = -1;
	int32 PreviousScreenshotDelegateValue = 1;
	bool bScreenshotDelegateCVarCaptured = false;
	double SessionStartSeconds = 0.0;
	double PhaseStartSeconds = 0.0;
	double WarmupStartSeconds = 0.0;
	double RequestStartSeconds = 0.0;
	double LastDiagnosticSeconds = 0.0;
	ACameraActor* Camera = nullptr;
	TArray<TObjectPtr<AActor>> TransientActors;
	TMap<FString, TArray<TObjectPtr<AActor>>> FamilyActors;
	TMap<FString, FBox> FamilyBounds;
	TArray<FCaptureRecord> PilotRecords;
	TArray<FCaptureRecord> ViewRecords;
	FDelegateHandle ScreenshotDelegateHandle;
};
