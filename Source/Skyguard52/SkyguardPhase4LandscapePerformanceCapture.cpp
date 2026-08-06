#include "SkyguardPhase4LandscapePerformanceCapture.h"

#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/DateTime.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "ProfilingDebugging/CsvProfiler.h"
#include "RHI.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

namespace
{
	const TCHAR* RequiredContractId =
		TEXT("P4.5-M01-LANDSCAPE-VISIBLE-005");
	constexpr double CsvStartActivationTimeoutSeconds = 5.0;
	constexpr double CsvFlushGraceSeconds = 2.0;
}

void USkyguardPhase4LandscapePerformanceCapture::Initialize(
	FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	const TCHAR* CommandLine = FCommandLine::Get();
	FParse::Value(
		CommandLine,
		TEXT("SkyguardP45ProfileContractId="),
		ContractId);
	FParse::Value(
		CommandLine,
		TEXT("SkyguardP45ProfileRunId="),
		RunId);
	FParse::Value(
		CommandLine,
		TEXT("SkyguardP45ProfileExpectedMap="),
		ExpectedMap);
	FParse::Value(
		CommandLine,
		TEXT("SkyguardP45ProfileReceipt="),
		ReceiptPath);
	FParse::Value(
		CommandLine,
		TEXT("SkyguardP45ProfileWarmupSeconds="),
		WarmupSeconds);
	FParse::Value(
		CommandLine,
		TEXT("SkyguardP45ProfileMeasuredSeconds="),
		MeasuredSeconds);
	bRequested =
		ContractId == RequiredContractId
		&& !RunId.IsEmpty()
		&& !ExpectedMap.IsEmpty()
		&& !ReceiptPath.IsEmpty()
		&& FMath::IsNearlyEqual(WarmupSeconds, 30.0, 0.001)
		&& FMath::IsNearlyEqual(MeasuredSeconds, 60.0, 0.001);
}

void USkyguardPhase4LandscapePerformanceCapture::Deinitialize()
{
	if ((bMeasurementStartRequested || bMeasurementStarted)
		&& !bStopRequested
		&& FCsvProfiler::Get()->IsCapturing())
	{
		if (UWorld* World = GetWorld(); GEngine && World)
		{
			GEngine->Exec(World, TEXT("csvprofile stop"));
		}
	}
	Super::Deinitialize();
}

TStatId USkyguardPhase4LandscapePerformanceCapture::GetStatId() const
{
	RETURN_QUICK_DECLARE_CYCLE_STAT(
		USkyguardPhase4LandscapePerformanceCapture,
		STATGROUP_Tickables);
}

bool USkyguardPhase4LandscapePerformanceCapture::IsTickable() const
{
	return bRequested && !bFinalized;
}

void USkyguardPhase4LandscapePerformanceCapture::Tick(float DeltaTime)
{
	if (!bWarmupStarted)
	{
		FString ReadinessIssue;
		if (IsWorldReady(ReadinessIssue))
		{
			BeginWarmup();
		}
		return;
	}

	const double Now = FPlatformTime::Seconds();
	if (!bMeasurementStarted)
	{
		if (!bMeasurementStartRequested
			&& Now - WarmupStartPlatformSeconds >= WarmupSeconds)
		{
			RequestMeasurementStart();
			return;
		}
		if (bMeasurementStartRequested
			&& FCsvProfiler::Get()->IsCapturing())
		{
			ConfirmMeasurementStart();
			return;
		}
		if (bMeasurementStartRequested
			&& Now - MeasurementStartRequestPlatformSeconds
				>= CsvStartActivationTimeoutSeconds)
		{
			FailMeasurementStart(
				TEXT("CSV profiler start command did not activate within five seconds."));
		}
		return;
	}
	if (!bStopRequested
		&& Now - MeasurementStartPlatformSeconds >= MeasuredSeconds)
	{
		RequestMeasurementStop();
		return;
	}
	if (bStopRequested
		&& Now - StopRequestPlatformSeconds >= CsvFlushGraceSeconds)
	{
		FinishAfterCsvFlush();
	}
}

bool USkyguardPhase4LandscapePerformanceCapture::IsWorldReady(
	FString& OutIssue) const
{
	const UWorld* World = GetWorld();
	if (!World || !World->HasBegunPlay())
	{
		OutIssue = TEXT("World has not begun play.");
		return false;
	}
	if (World->GetOutermost()->GetName() != ExpectedMap)
	{
		OutIssue = TEXT("Loaded map differs from governed expected map.");
		return false;
	}
	if (!GEngine || !GEngine->GameViewport
		|| !GEngine->GameViewport->Viewport)
	{
		OutIssue = TEXT("Game viewport is unavailable.");
		return false;
	}
	if (GEngine->GameViewport->Viewport->GetSizeXY() != FIntPoint(1920, 1080))
	{
		OutIssue = TEXT("Viewport is not exact 1920x1080.");
		return false;
	}
	const APlayerController* Controller = World->GetFirstPlayerController();
	if (!Controller || !Controller->PlayerCameraManager)
	{
		OutIssue = TEXT("Player camera manager is unavailable.");
		return false;
	}
	if (!FApp::GetGraphicsRHI().Contains(TEXT("D3D12"))
		|| FString(LexToString(GMaxRHIFeatureLevel)) != TEXT("SM6"))
	{
		OutIssue = TEXT("Active RHI is not D3D12 SM6.");
		return false;
	}
	return true;
}

void USkyguardPhase4LandscapePerformanceCapture::BeginWarmup()
{
	bWarmupStarted = true;
	WarmupStartPlatformSeconds = FPlatformTime::Seconds();
	WarmupStartedAtUtc = FDateTime::UtcNow();
	UE_LOG(
		LogTemp,
		Display,
		TEXT("[P4_PROFILE_WARMUP_BEGIN] contract=%s run=%s seconds=30"),
		*ContractId,
		*RunId);
}

void USkyguardPhase4LandscapePerformanceCapture::RequestMeasurementStart()
{
	UWorld* World = GetWorld();
	if (!World || !GEngine)
	{
		FailMeasurementStart(TEXT("World unavailable at CSV start."));
		return;
	}

	FCsvProfiler::SetMetadata(TEXT("contract_id"), *ContractId);
	FCsvProfiler::SetMetadata(TEXT("run_id"), *RunId);
	FCsvProfiler::SetMetadata(TEXT("warmup_seconds"), TEXT("30"));
	FCsvProfiler::SetMetadata(TEXT("measured_seconds"), TEXT("60"));
	FCsvProfiler::SetMetadata(TEXT("startup_frames_excluded"), TEXT("true"));
	UE_LOG(
		LogTemp,
		Display,
		TEXT("[P4_PROFILE_WARMUP_COMPLETE] contract=%s run=%s"),
		*ContractId,
		*RunId);
	UE_LOG(
		LogTemp,
		Display,
		TEXT("[P4_PROFILE_MEASURED_START_REQUESTED] contract=%s run=%s"),
		*ContractId,
		*RunId);
	GEngine->Exec(World, TEXT("csvprofile start"));
	bMeasurementStartRequested = true;
	MeasurementStartRequestPlatformSeconds = FPlatformTime::Seconds();
	MeasurementStartRequestedAtUtc = FDateTime::UtcNow();
}

void USkyguardPhase4LandscapePerformanceCapture::ConfirmMeasurementStart()
{
	bMeasurementStarted = true;
	MeasurementStartPlatformSeconds = FPlatformTime::Seconds();
	MeasurementStartedAtUtc = FDateTime::UtcNow();
	UE_LOG(
		LogTemp,
		Display,
		TEXT("[P4_PROFILE_MEASURED_START] contract=%s run=%s seconds=60"),
		*ContractId,
		*RunId);
}

void USkyguardPhase4LandscapePerformanceCapture::FailMeasurementStart(
	const FString& Issue)
{
	bFinalized = true;
	WriteReceipt(TEXT("FAIL"), Issue);
	FPlatformMisc::RequestExitWithStatus(
		false,
		1,
		TEXT("SkyguardP45CsvStartFailure"));
}

void USkyguardPhase4LandscapePerformanceCapture::RequestMeasurementStop()
{
	UWorld* World = GetWorld();
	UE_LOG(
		LogTemp,
		Display,
		TEXT("[P4_PROFILE_MEASURED_STOP] contract=%s run=%s"),
		*ContractId,
		*RunId);
	if (World && GEngine)
	{
		GEngine->Exec(World, TEXT("csvprofile stop"));
	}
	bStopRequested = true;
	StopRequestPlatformSeconds = FPlatformTime::Seconds();
}

void USkyguardPhase4LandscapePerformanceCapture::FinishAfterCsvFlush()
{
	const bool bStillCapturing = FCsvProfiler::Get()->IsCapturing();
	const bool bWritten = WriteReceipt(
		bStillCapturing ? TEXT("FAIL") : TEXT("PASS"),
		bStillCapturing
			? TEXT("CSV profiler remained active after the flush boundary.")
			: FString());
	bFinalized = true;
	FPlatformMisc::RequestExitWithStatus(
		false,
		(!bStillCapturing && bWritten) ? 0 : 1,
		TEXT("SkyguardP45LandscapeProfileComplete"));
}

bool USkyguardPhase4LandscapePerformanceCapture::WriteReceipt(
	const FString& Gate,
	const FString& Issue) const
{
	if (ReceiptPath.IsEmpty())
	{
		return false;
	}
	IFileManager::Get().MakeDirectory(*FPaths::GetPath(ReceiptPath), true);
	const UWorld* World = GetWorld();
	const TSharedRef<FJsonObject> Receipt = MakeShared<FJsonObject>();
	Receipt->SetStringField(
		TEXT("schema"),
		TEXT("skyguard.phase4.m01-landscape-profile-receipt.v1"));
	Receipt->SetStringField(TEXT("contract_id"), ContractId);
	Receipt->SetStringField(TEXT("run_id"), RunId);
	Receipt->SetStringField(TEXT("gate"), Gate);
	Receipt->SetStringField(
		TEXT("map"),
		World ? World->GetOutermost()->GetName() : TEXT("None"));
	Receipt->SetStringField(TEXT("rhi"), FApp::GetGraphicsRHI());
	Receipt->SetStringField(
		TEXT("feature_level"),
		LexToString(GMaxRHIFeatureLevel));
	Receipt->SetBoolField(TEXT("same_process_warmup_and_measurement"), true);
	Receipt->SetBoolField(TEXT("startup_frames_excluded"), true);
	Receipt->SetNumberField(TEXT("warmup_seconds"), WarmupSeconds);
	Receipt->SetNumberField(TEXT("measured_seconds"), MeasuredSeconds);
	Receipt->SetNumberField(
		TEXT("csv_start_activation_timeout_seconds"),
		CsvStartActivationTimeoutSeconds);
	Receipt->SetStringField(
		TEXT("warmup_started_at_utc"),
		WarmupStartedAtUtc.ToIso8601());
	Receipt->SetStringField(
		TEXT("measurement_start_requested_at_utc"),
		MeasurementStartRequestedAtUtc.ToIso8601());
	Receipt->SetStringField(
		TEXT("measurement_started_at_utc"),
		MeasurementStartedAtUtc.ToIso8601());
	Receipt->SetStringField(
		TEXT("completed_at_utc"),
		FDateTime::UtcNow().ToIso8601());
	Receipt->SetStringField(TEXT("issue"), Issue);

	FString Json;
	const TSharedRef<TJsonWriter<>> Writer =
		TJsonWriterFactory<>::Create(&Json);
	return FJsonSerializer::Serialize(Receipt, Writer)
		&& FFileHelper::SaveStringToFile(
			Json,
			*ReceiptPath,
			FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}
