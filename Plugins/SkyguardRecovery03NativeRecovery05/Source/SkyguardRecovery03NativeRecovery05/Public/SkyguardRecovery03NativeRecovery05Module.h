#pragma once

#include "Containers/Ticker.h"
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "UObject/WeakObjectPtr.h"

class ALandscapeProxy;
class UMaterialInterface;

class FSkyguardRecovery03NativeRecovery05Module final : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    enum class EPhase : uint8
    {
        Inert,
        Preflight,
        ShaderWait,
        Warmup,
        Measure,
        Capture,
        Terminal
    };

public:
    struct FCaptureSpec
    {
        const TCHAR* Id;
        FVector Location;
        FRotator Rotation;
        int32 MinimumGapTicks;
    };

    struct FCaptureRecord
    {
        FString Id;
        FString File;
        int64 Bytes = 0;
        FString Sha256;
        int64 Tick = 0;
    };

private:
    bool Tick(float DeltaSeconds);
    bool ParseAuthorization();
    bool VerifyImmutableInputs(FString& OutIssue) const;
    bool VerifyWorldAndAssets(FString& OutIssue);
    bool CreateFreshOutput(FString& OutIssue);
    bool BindTransientMaterial(FString& OutIssue);
    bool IsShaderReady(FString& OutIssue, int32& OutFinishedResources, int32& OutValidShaderMaps) const;
    bool CaptureCurrent(FString& OutIssue);
    bool RestoreMaterial(FString& OutIssue);
    bool VerifyPng(const FString& File, FString& OutIssue, int64& OutBytes, FString& OutHash) const;
    bool VerifyFile(const FString& File, int64 Bytes, const FString& Sha256, FString& OutIssue) const;
    FString HashFile(const FString& File) const;
    FString MaterialIdentity(UMaterialInterface* Material) const;
    void AppendHeartbeat(const FString& Event);
    void WriteFrameSamples() const;
    void WriteCaptureReceipt(bool bPassed, const FString& Issue) const;
    void WriteRestorationReceipt(bool bPassed, const FString& Issue) const;
    bool WriteTerminalReceipt(bool bPassed, const FString& Issue, int32 ExitCode) const;
    void CompleteTerminal(bool bPassed, const FString& Issue, int32 ExitCode);

    FTSTicker::FDelegateHandle TickerHandle;
    EPhase Phase = EPhase::Inert;
    FString ContractId;
    FString AuthorizationToken;
    FString ExpectedMap;
    FString AttemptRoot;
    FString ProofRoot;
    FString CaptureRoot;
    TWeakObjectPtr<ALandscapeProxy> Landscape;
    TWeakObjectPtr<UMaterialInterface> OriginalMaterial;
    TWeakObjectPtr<UMaterialInterface> ValidationMaterial;
    FString OriginalMaterialIdentity;
    FString RestoredMaterialIdentity;
    bool bAuthorized = false;
    bool bMaterialBound = false;
    bool bRestorationVerified = false;
    bool bTerminalReceiptWritten = false;
    bool bExitRequested = false;
    int64 TickOrdinal = 0;
    int32 StableShaderPolls = 0;
    int32 CaptureIndex = 0;
    int32 CaptureGapTicks = 0;
    double StartedSeconds = 0.0;
    double PhaseStartedSeconds = 0.0;
    TArray<double> FrameMilliseconds;
    TArray<double> GpuMilliseconds;
    TArray<uint64> WorkingSetBytes;
    TArray<uint64> TextureMemoryBytes;
    TArray<int64> TotalGpuMemoryBytes;
    TArray<int64> AvailableTextureMemoryBytes;
    TArray<FCaptureRecord> Captures;
};
