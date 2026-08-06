#include "SkyguardInputCombatPerformanceCapture.h"

#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/DateTime.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "ProfilingDebugging/MiscTrace.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

namespace
{
	constexpr int32 MinimumRepeatedRifleShots = 5;

	const TPair<FName, int32> RequiredEvents[] = {
		{TEXT("aim_input"), 1},
		{TEXT("ads_started"), 1},
		{TEXT("ads_left_fire_overlap"), 1},
		{TEXT("ads_ended"), 1},
		{TEXT("rifle_shot"), MinimumRepeatedRifleShots},
		{TEXT("weapon_switch"), 1},
		{TEXT("igla_lock_acquired"), 1},
		{TEXT("igla_launch"), 1},
		{TEXT("igla_impact"), 1},
		{TEXT("drone_breakup"), 1},
		{TEXT("drone_breakup_cleanup"), 1},
		{TEXT("boss_weak_point_destroyed"), 1},
		{TEXT("boss_destroyed"), 1},
		{TEXT("boss_destruction_cleanup"), 1},
		{TEXT("weather_visibility_transition"), 1},
		{TEXT("weather_visibility_transition_complete"), 1},
	};
}

void USkyguardInputCombatPerformanceCapture::Initialize(
	FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);

	const TCHAR* CommandLine = FCommandLine::Get();
	FParse::Value(CommandLine, TEXT("SkyguardCombatPerfRunId="), RunId);
	FParse::Value(CommandLine, TEXT("SkyguardCombatPerfKind="), RunKind);
	FParse::Value(
		CommandLine,
		TEXT("SkyguardCombatPerfDurationSeconds="),
		RequestedDurationSeconds);
	FParse::Value(
		CommandLine,
		TEXT("SkyguardCombatPerfReceipt="),
		ReceiptPath);
	FParse::Value(
		CommandLine,
		TEXT("SkyguardCombatPerfExpectedMap="),
		ExpectedMap);

	bCaptureRequested =
		!RunId.IsEmpty() &&
		(RunKind == TEXT("combat") || RunKind == TEXT("soak")) &&
		RequestedDurationSeconds > 0.0 &&
		!ReceiptPath.IsEmpty() &&
		!ExpectedMap.IsEmpty();
}

void USkyguardInputCombatPerformanceCapture::Deinitialize()
{
	Events.Reset();
	Super::Deinitialize();
}

TStatId USkyguardInputCombatPerformanceCapture::GetStatId() const
{
	RETURN_QUICK_DECLARE_CYCLE_STAT(
		USkyguardInputCombatPerformanceCapture,
		STATGROUP_Tickables);
}

bool USkyguardInputCombatPerformanceCapture::IsTickable() const
{
	return bCaptureRequested && !bFinalized;
}

void USkyguardInputCombatPerformanceCapture::Tick(float DeltaTime)
{
	if (!bMeasurementStarted)
	{
		TryStartMeasurement();
		return;
	}
	if (FPlatformTime::Seconds() - StartPlatformSeconds >= RequestedDurationSeconds)
	{
		CompleteMeasurement();
		return;
	}
	UpdateTraceWindows(FPlatformTime::Seconds() - StartPlatformSeconds);
}

USkyguardInputCombatPerformanceCapture*
USkyguardInputCombatPerformanceCapture::Resolve(const UObject* WorldContext)
{
	if (!WorldContext)
	{
		return nullptr;
	}
	UWorld* World = WorldContext->GetWorld();
	return World
		? World->GetSubsystem<USkyguardInputCombatPerformanceCapture>()
		: nullptr;
}

void USkyguardInputCombatPerformanceCapture::RecordPlayerEvent(
	const UObject* WorldContext,
	const FName EventName)
{
	if (USkyguardInputCombatPerformanceCapture* Capture = Resolve(WorldContext))
	{
		Capture->RecordEvent(EventName, true);
	}
}

void USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
	const UObject* WorldContext,
	const FName EventName)
{
	if (USkyguardInputCombatPerformanceCapture* Capture = Resolve(WorldContext))
	{
		Capture->RecordEvent(EventName, false);
	}
}

bool USkyguardInputCombatPerformanceCapture::IsCaptureActive(
	const UObject* WorldContext)
{
	const USkyguardInputCombatPerformanceCapture* Capture = Resolve(WorldContext);
	return Capture &&
		Capture->bCaptureRequested &&
		Capture->bMeasurementStarted &&
		!Capture->bFinalized;
}

void USkyguardInputCombatPerformanceCapture::TryStartMeasurement()
{
	UWorld* World = GetWorld();
	if (!World || !World->HasBegunPlay())
	{
		return;
	}

	const FString LoadedMap = World->GetOutermost()->GetName();
	if (LoadedMap != ExpectedMap)
	{
		return;
	}

	StartPlatformSeconds = FPlatformTime::Seconds();
	StartedAtUtc = FDateTime::UtcNow();
	bMeasurementStarted = true;
	if (GEngine)
	{
		GEngine->Exec(World, TEXT("csvprofile start"));
	}
}

void USkyguardInputCombatPerformanceCapture::RecordEvent(
	const FName EventName,
	const bool bFromPlayerInput)
{
	if (!bMeasurementStarted || bFinalized || EventName.IsNone())
	{
		return;
	}
	const double Seconds = FPlatformTime::Seconds() - StartPlatformSeconds;
	if (Seconds < 0.0 || Seconds > RequestedDurationSeconds)
	{
		return;
	}
	FRecordedEvent& Event = Events.AddDefaulted_GetRef();
	Event.Name = EventName;
	Event.SecondsFromStart = Seconds;
	bObservedPlayerInput |= bFromPlayerInput;

	if (EventName == TEXT("ads_started"))
	{
		BeginTraceWindow(
			TEXT("ads_rifle"),
			TEXT("Skyguard.Perf.ADS_Rifle"),
			TEXT("Skyguard.Perf.ADS_Rifle.Begin"),
			TEXT("Skyguard.Perf.ADS_Rifle.End"),
			1.0,
			10.0);
	}
	else if (EventName == TEXT("ads_ended"))
	{
		RequestTraceWindowEnd(TEXT("ads_rifle"), 0.0);
	}
	else if (EventName == TEXT("igla_lock_acquired"))
	{
		BeginTraceWindow(
			TEXT("igla_launch"),
			TEXT("Skyguard.Perf.Igla"),
			TEXT("Skyguard.Perf.Igla.Begin"),
			TEXT("Skyguard.Perf.Igla.End"),
			1.0,
			30.0);
	}
	else if (EventName == TEXT("igla_impact"))
	{
		RequestTraceWindowEnd(TEXT("igla_launch"), 1.0);
	}
	else if (EventName == TEXT("drone_breakup"))
	{
		BeginTraceWindow(
			TEXT("drone_breakup"),
			TEXT("Skyguard.Perf.DroneBreakup"),
			TEXT("Skyguard.Perf.DroneBreakup.Begin"),
			TEXT("Skyguard.Perf.DroneBreakup.End"),
			1.0,
			8.0);
	}
	else if (EventName == TEXT("drone_breakup_cleanup"))
	{
		RequestTraceWindowEnd(TEXT("drone_breakup"), 0.0);
	}
	else if (EventName == TEXT("boss_weak_point_destroyed"))
	{
		BeginTraceWindow(
			TEXT("boss_destruction"),
			TEXT("Skyguard.Perf.BossDestruction"),
			TEXT("Skyguard.Perf.BossDestruction.Begin"),
			TEXT("Skyguard.Perf.BossDestruction.End"),
			1.0,
			30.0);
	}
	else if (EventName == TEXT("boss_destroyed"))
	{
		// The region remains open until the bounded debris cleanup callback.
	}
	else if (EventName == TEXT("boss_destruction_cleanup"))
	{
		RequestTraceWindowEnd(TEXT("boss_destruction"), 0.0);
	}
	else if (EventName == TEXT("weather_visibility_transition"))
	{
		BeginTraceWindow(
			TEXT("weather_fast_camera"),
			TEXT("Skyguard.Perf.WeatherFastCamera"),
			TEXT("Skyguard.Perf.WeatherFastCamera.Begin"),
			TEXT("Skyguard.Perf.WeatherFastCamera.End"),
			1.0,
			30.0);
	}
	else if (EventName == TEXT("weather_visibility_transition_complete"))
	{
		RequestTraceWindowEnd(TEXT("weather_fast_camera"), 0.0);
	}
}

void USkyguardInputCombatPerformanceCapture::UpdateTraceWindows(
	const double SecondsFromStart)
{
	TArray<FName> WindowsToEnd;
	for (const TPair<FName, FTraceWindowState>& Pair : TraceWindows)
	{
		const FTraceWindowState& Window = Pair.Value;
		if (!Window.bActive)
		{
			continue;
		}
		const double EndThreshold = FMath::Min(
			Window.RequestedEndSeconds,
			Window.MaximumEndSeconds);
		if (
			SecondsFromStart >= Window.EarliestEndSeconds &&
			SecondsFromStart >= EndThreshold)
		{
			WindowsToEnd.Add(Pair.Key);
		}
	}
	for (const FName WindowId : WindowsToEnd)
	{
		EndTraceWindow(WindowId);
	}
}

void USkyguardInputCombatPerformanceCapture::BeginTraceWindow(
	const FName WindowId,
	const TCHAR* RegionName,
	const TCHAR* BeginBookmark,
	const TCHAR* EndBookmark,
	const double MinimumDuration,
	const double MaximumDuration,
	const double AutomaticEndDelay)
{
	if (WindowId.IsNone() || !RegionName || !BeginBookmark || !EndBookmark)
	{
		return;
	}
	FTraceWindowState& Window = TraceWindows.FindOrAdd(WindowId);
	if (Window.bActive)
	{
		return;
	}
	const double Seconds = FPlatformTime::Seconds() - StartPlatformSeconds;
	Window.RegionName = RegionName;
	Window.EndBookmark = EndBookmark;
	Window.StartedSeconds = Seconds;
	Window.EarliestEndSeconds = Seconds + FMath::Max(1.0, MinimumDuration);
	Window.MaximumEndSeconds = Seconds + FMath::Clamp(MaximumDuration, 1.0, 30.0);
	Window.RequestedEndSeconds = FMath::IsFinite(AutomaticEndDelay)
		? Seconds + FMath::Max(AutomaticEndDelay, MinimumDuration)
		: TNumericLimits<double>::Max();
	Window.RegionId = TRACE_BEGIN_REGION_WITH_ID(RegionName, TEXT("Skyguard.Perf"));
	Window.bActive = true;
	TRACE_BOOKMARK(TEXT("%s"), BeginBookmark);
}

void USkyguardInputCombatPerformanceCapture::RequestTraceWindowEnd(
	const FName WindowId,
	const double DelaySeconds)
{
	if (FTraceWindowState* Window = TraceWindows.Find(WindowId))
	{
		if (Window->bActive)
		{
			const double Seconds = FPlatformTime::Seconds() - StartPlatformSeconds;
			Window->RequestedEndSeconds = FMath::Min(
				Window->RequestedEndSeconds,
				Seconds + FMath::Max(0.0, DelaySeconds));
		}
	}
}

void USkyguardInputCombatPerformanceCapture::EndTraceWindow(
	const FName WindowId)
{
	FTraceWindowState* Window = TraceWindows.Find(WindowId);
	if (!Window || !Window->bActive)
	{
		return;
	}
	TRACE_BOOKMARK(TEXT("%s"), *Window->EndBookmark);
	TRACE_END_REGION_WITH_ID(Window->RegionId);
	Window->bActive = false;
}

void USkyguardInputCombatPerformanceCapture::EndAllTraceWindows()
{
	TArray<FName> ActiveWindowIds;
	for (const TPair<FName, FTraceWindowState>& Pair : TraceWindows)
	{
		if (Pair.Value.bActive)
		{
			ActiveWindowIds.Add(Pair.Key);
		}
	}
	for (const FName WindowId : ActiveWindowIds)
	{
		EndTraceWindow(WindowId);
	}
}

bool USkyguardInputCombatPerformanceCapture::HasRequiredEventCounts(
	TArray<FString>& OutIssues) const
{
	for (const TPair<FName, int32>& Requirement : RequiredEvents)
	{
		int32 Count = 0;
		for (const FRecordedEvent& Event : Events)
		{
			if (Event.Name == Requirement.Key)
			{
				++Count;
			}
		}
		if (Count < Requirement.Value)
		{
			OutIssues.Add(FString::Printf(
				TEXT("%s requires %d event(s); observed %d"),
				*Requirement.Key.ToString(),
				Requirement.Value,
				Count));
		}
	}
	if (!bObservedPlayerInput)
	{
		OutIssues.Add(TEXT("No event arrived through a bound player-input wrapper."));
	}
	return OutIssues.IsEmpty();
}

void USkyguardInputCombatPerformanceCapture::CompleteMeasurement()
{
	if (bFinalized)
	{
		return;
	}
	bFinalized = true;
	EndAllTraceWindows();
	UWorld* World = GetWorld();
	if (GEngine && World)
	{
		GEngine->Exec(World, TEXT("csvprofile stop"));
	}

	TArray<FString> Issues;
	HasRequiredEventCounts(Issues);
	const bool bEvidencePassed = Issues.IsEmpty();
	const bool bWritten = WriteReceipt(
		TEXT("COMPLETE"),
		bEvidencePassed ? TEXT("PASS") : TEXT("FAIL"),
		Issues);
	FPlatformMisc::RequestExitWithStatus(
		false,
		bWritten ? 0 : 1,
		TEXT("SkyguardInputCombatPerformanceCaptureComplete"));
}

bool USkyguardInputCombatPerformanceCapture::WriteReceipt(
	const FString& State,
	const FString& Gate,
	const TArray<FString>& Issues) const
{
	if (ReceiptPath.IsEmpty())
	{
		return false;
	}
	const FString Directory = FPaths::GetPath(ReceiptPath);
	if (!Directory.IsEmpty())
	{
		IFileManager::Get().MakeDirectory(*Directory, true);
	}

	const UWorld* World = GetWorld();
	const FString LoadedMap = World
		? World->GetOutermost()->GetName()
		: TEXT("None");
	FIntPoint Resolution = FIntPoint::ZeroValue;
	if (GEngine && GEngine->GameViewport && GEngine->GameViewport->Viewport)
	{
		Resolution = GEngine->GameViewport->Viewport->GetSizeXY();
	}

	const TSharedRef<FJsonObject> Receipt = MakeShared<FJsonObject>();
	Receipt->SetStringField(
		TEXT("schema"),
		TEXT("skyguard.m01.input-combat.runtime-receipt.v1"));
	Receipt->SetStringField(TEXT("state"), State);
	Receipt->SetStringField(TEXT("gate"), Gate);
	Receipt->SetStringField(TEXT("run_id"), RunId);
	Receipt->SetStringField(TEXT("kind"), RunKind);
	Receipt->SetStringField(TEXT("map"), LoadedMap);
	Receipt->SetStringField(TEXT("rhi"), FApp::GetGraphicsRHI());
	Receipt->SetStringField(
		TEXT("input_source"),
		bObservedPlayerInput ? TEXT("PlayerInput") : TEXT("None"));
	Receipt->SetBoolField(TEXT("automation_injected"), false);

	const TSharedRef<FJsonObject> ResolutionObject = MakeShared<FJsonObject>();
	ResolutionObject->SetNumberField(TEXT("x"), Resolution.X);
	ResolutionObject->SetNumberField(TEXT("y"), Resolution.Y);
	Receipt->SetObjectField(TEXT("resolution"), ResolutionObject);

	const TSharedRef<FJsonObject> Window = MakeShared<FJsonObject>();
	Window->SetStringField(
		TEXT("started_at_utc"),
		StartedAtUtc.ToIso8601());
	Window->SetStringField(
		TEXT("ended_at_utc"),
		FDateTime::UtcNow().ToIso8601());
	Window->SetNumberField(
		TEXT("duration_seconds"),
		FPlatformTime::Seconds() - StartPlatformSeconds);
	Receipt->SetObjectField(TEXT("measurement_window"), Window);

	TArray<TSharedPtr<FJsonValue>> EventValues;
	for (const FRecordedEvent& Event : Events)
	{
		const TSharedRef<FJsonObject> EventObject = MakeShared<FJsonObject>();
		EventObject->SetStringField(TEXT("name"), Event.Name.ToString());
		EventObject->SetNumberField(
			TEXT("seconds_from_measurement_start"),
			Event.SecondsFromStart);
		EventValues.Add(MakeShared<FJsonValueObject>(EventObject));
	}
	Receipt->SetArrayField(TEXT("events"), EventValues);

	TArray<TSharedPtr<FJsonValue>> IssueValues;
	for (const FString& Issue : Issues)
	{
		IssueValues.Add(MakeShared<FJsonValueString>(Issue));
	}
	Receipt->SetArrayField(TEXT("issues"), IssueValues);

	FString Json;
	const TSharedRef<TJsonWriter<>> Writer =
		TJsonWriterFactory<>::Create(&Json);
	return FJsonSerializer::Serialize(Receipt, Writer) &&
		FFileHelper::SaveStringToFile(
			Json,
			*ReceiptPath,
			FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}
