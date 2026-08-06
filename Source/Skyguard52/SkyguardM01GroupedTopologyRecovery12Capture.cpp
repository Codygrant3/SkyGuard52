#include "SkyguardM01GroupedTopologyRecovery12Capture.h"

#include "Algo/AllOf.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/LightComponent.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Components/SkyLightComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/DirectionalLight.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/SkyLight.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "HighResScreenshot.h"
#include "ImageUtils.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "RHI.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "ShaderCompiler.h"
#include "Slate/SceneViewport.h"
#include "UnrealClient.h"

DEFINE_LOG_CATEGORY_STATIC(LogSkyguardRecovery12, Log, All);

namespace
{
	const TCHAR* RequiredContractId =
		TEXT("M01-HERO-GROUPED-TOPOLOGY-ATTEMPT03-RECOVERY12");
	constexpr int32 RequiredWidth = 2048;
	constexpr int32 RequiredHeight = 2048;
	constexpr int32 RequiredConsecutiveReadyFrames = 30;
	constexpr int32 RequiredWarmupFrames = 120;
	constexpr double RequiredWarmupSeconds = 5.0;
	constexpr int32 RequiredSettleFrames = 30;
	constexpr double WorldReadinessTimeoutSeconds = 45.0;
	constexpr double ScreenshotTimeoutSeconds = 45.0;
	constexpr int32 FilesystemStableFramesRequired = 3;
	constexpr int64 MinimumPngBytes = 25000;
	constexpr double AbsoluteSessionTimeoutSeconds = 300.0;
	constexpr double DiagnosticIntervalSeconds = 2.0;
	constexpr uint8 ActiveThreshold = 8;
	constexpr double MinimumActiveFraction = 0.02;
	constexpr double MaximumClippedFraction = 0.02;
	constexpr int32 MinimumMaximumChannel = 64;
	constexpr int32 MinimumUniqueColors = 64;
	constexpr double MinimumP50 = 35.0;
	constexpr double MaximumP50 = 210.0;
	constexpr double MinimumP95 = 100.0;
	constexpr double MaximumP95 = 248.0;
	constexpr double MinimumDynamicRange = 35.0;

	const TArray<TPair<FString, FString>> GovernedViews = {
		{TEXT("Pathfinder"), TEXT("three_quarter")},
		{TEXT("Pathfinder"), TEXT("grazing_port")},
		{TEXT("Pathfinder"), TEXT("grazing_starboard")},
		{TEXT("Lighthouse"), TEXT("three_quarter")},
		{TEXT("Lighthouse"), TEXT("grazing_port")},
		{TEXT("Lighthouse"), TEXT("grazing_starboard")},
		{TEXT("RadarPost"), TEXT("three_quarter")},
		{TEXT("RadarPost"), TEXT("grazing_port")},
		{TEXT("RadarPost"), TEXT("grazing_starboard")}
	};

	double HistogramPercentile(
		const TArray<int64>& Histogram,
		const double Fraction)
	{
		int64 Total = 0;
		for (const int64 Count : Histogram)
		{
			Total += Count;
		}
		if (Total <= 0)
		{
			return 0.0;
		}
		const double Target = Fraction * static_cast<double>(Total - 1);
		int64 Cumulative = 0;
		for (int32 Value = 0; Value < Histogram.Num(); ++Value)
		{
			if (static_cast<double>(Cumulative + Histogram[Value]) > Target)
			{
				return static_cast<double>(Value);
			}
			Cumulative += Histogram[Value];
		}
		return 255.0;
	}

	TSharedRef<FJsonObject> RecordToJson(
		const USkyguardM01GroupedTopologyRecovery12Capture::FCaptureRecord&
			Record)
	{
		const TSharedRef<FJsonObject> Json = MakeShared<FJsonObject>();
		Json->SetStringField(TEXT("family"), Record.Family);
		Json->SetStringField(TEXT("view"), Record.View);
		Json->SetStringField(TEXT("path"), Record.Path);
		Json->SetStringField(
			TEXT("completion_method"),
			Record.CompletionMethod);
		Json->SetNumberField(TEXT("width"), Record.Width);
		Json->SetNumberField(TEXT("height"), Record.Height);
		Json->SetNumberField(
			TEXT("active_pixel_fraction"),
			Record.ActivePixelFraction);
		Json->SetNumberField(
			TEXT("active_clipped_fraction"),
			Record.ActiveClippedFraction);
		Json->SetNumberField(TEXT("active_p05"), Record.ActiveP05);
		Json->SetNumberField(TEXT("active_p50"), Record.ActiveP50);
		Json->SetNumberField(TEXT("active_p95"), Record.ActiveP95);
		Json->SetNumberField(
			TEXT("active_dynamic_range"),
			Record.ActiveDynamicRange);
		Json->SetNumberField(
			TEXT("maximum_channel_value"),
			Record.MaximumChannel);
		Json->SetNumberField(
			TEXT("unique_color_count_capped_at_4096"),
			Record.UniqueColorCount);
		Json->SetBoolField(
			TEXT("liveness_passed"),
			Record.bLivenessPassed);
		Json->SetBoolField(
			TEXT("hard_bounds_passed"),
			Record.bHardBoundsPassed);
		return Json;
	}
}

void USkyguardM01GroupedTopologyRecovery12Capture::Initialize(
	FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	FParse::Value(
		FCommandLine::Get(),
		TEXT("SkyguardM01Recovery12ContractId="),
		ContractId);
	FParse::Value(
		FCommandLine::Get(),
		TEXT("SkyguardM01Recovery12ExpectedMap="),
		ExpectedMap);
	FParse::Value(
		FCommandLine::Get(),
		TEXT("SkyguardM01Recovery12Output="),
		OutputRoot);
	bRequested =
		ContractId == RequiredContractId
		&& !ExpectedMap.IsEmpty()
		&& !OutputRoot.IsEmpty();
	if (bRequested)
	{
		SessionStartSeconds = FPlatformTime::Seconds();
		PhaseStartSeconds = SessionStartSeconds;
		LastDiagnosticSeconds =
			SessionStartSeconds - DiagnosticIntervalSeconds;
		IConsoleVariable* ScreenshotDelegateCVar =
			IConsoleManager::Get().FindConsoleVariable(
				TEXT("r.ScreenshotDelegate"));
		if (!ScreenshotDelegateCVar)
		{
			InitializationFailure =
				TEXT("r.ScreenshotDelegate is unavailable.");
		}
		else
		{
			PreviousScreenshotDelegateValue =
				ScreenshotDelegateCVar->GetInt();
			bScreenshotDelegateCVarCaptured = true;
			ScreenshotDelegateCVar->Set(1, ECVF_SetByCode);
			ScreenshotDelegateHandle =
				UGameViewportClient::OnScreenshotCaptured().AddUObject(
					this,
					&USkyguardM01GroupedTopologyRecovery12Capture::
						HandleScreenshotCaptured);
		}
		UE_LOG(
			LogSkyguardRecovery12,
			Display,
			TEXT("[RECOVERY12][ACTIVATED] contract=%s output=%s"),
			*ContractId,
			*OutputRoot);
	}
}

void USkyguardM01GroupedTopologyRecovery12Capture::Deinitialize()
{
	if (ScreenshotDelegateHandle.IsValid())
	{
		UGameViewportClient::OnScreenshotCaptured().Remove(
			ScreenshotDelegateHandle);
	}
	GetHighResScreenshotConfig().SetFilename(FString());
	RestoreScreenshotDelegateCVar();
	RestoreVisibility();
	Super::Deinitialize();
}

TStatId USkyguardM01GroupedTopologyRecovery12Capture::GetStatId() const
{
	RETURN_QUICK_DECLARE_CYCLE_STAT(
		USkyguardM01GroupedTopologyRecovery12Capture,
		STATGROUP_Tickables);
}

bool USkyguardM01GroupedTopologyRecovery12Capture::IsTickable() const
{
	return bRequested
		&& Phase != EPhase::Finished
		&& Phase != EPhase::Failed;
}

void USkyguardM01GroupedTopologyRecovery12Capture::Tick(float DeltaTime)
{
	const double Now = FPlatformTime::Seconds();
	if (!InitializationFailure.IsEmpty())
	{
		Fail(InitializationFailure);
		return;
	}
	if (Now - SessionStartSeconds > AbsoluteSessionTimeoutSeconds)
	{
		Fail(FString::Printf(
			TEXT("Absolute session timeout in phase %s; last_issue=%s"),
			*PhaseName(),
			*LastReadinessIssue));
		return;
	}
	if (bScreenshotPending)
	{
		if (TryCompleteCurrentCaptureFromFilesystem())
		{
			return;
		}
		if (Now - RequestStartSeconds > ScreenshotTimeoutSeconds)
		{
			Fail(FString::Printf(
				TEXT(
					"High-resolution screenshot callback timeout; "
					"family=%s view=%s live_viewport=%s"),
				*PendingFamily,
				*PendingView,
				*GetLiveViewportSize().ToString()));
		}
		return;
	}

	if (Phase == EPhase::WaitForWorld)
	{
		FString Issue;
		if (!IsWorldRenderable(Issue))
		{
			LastReadinessIssue = Issue;
			ConsecutiveReadyFrames = 0;
			MaybeLogDiagnostic(Issue);
			if (Now - PhaseStartSeconds > WorldReadinessTimeoutSeconds)
			{
				Fail(FString::Printf(
					TEXT(
						"World readiness timeout after %.1fs: %s; "
						"live_viewport=%s"),
					Now - PhaseStartSeconds,
					*Issue,
					*GetLiveViewportSize().ToString()));
			}
			return;
		}
		LastReadinessIssue.Reset();
		++ConsecutiveReadyFrames;
		MaybeLogDiagnostic(TEXT("world_renderable"));
		if (ConsecutiveReadyFrames >= RequiredConsecutiveReadyFrames)
		{
			if (!ConfigureScene())
			{
				Fail(TEXT("Could not configure Recovery12 capture scene."));
				return;
			}
			WarmupStartSeconds = Now;
			PhaseStartSeconds = Now;
			Phase = EPhase::Warmup;
		}
		return;
	}

	if (Phase == EPhase::Warmup)
	{
		if (GShaderCompilingManager && GShaderCompilingManager->IsCompiling())
		{
			WarmupFrames = 0;
			WarmupStartSeconds = Now;
			MaybeLogDiagnostic(TEXT("shader_compilation_active"));
			return;
		}
		++WarmupFrames;
		MaybeLogDiagnostic(TEXT("warming_render_frames"));
		if (WarmupFrames >= RequiredWarmupFrames
			&& Now - WarmupStartSeconds >= RequiredWarmupSeconds)
		{
			if (!ConfigureView(TEXT("Pathfinder"), TEXT("three_quarter")))
			{
				Fail(TEXT("Could not configure Recovery12 pilot view."));
				return;
			}
			SettleFrames = 0;
			PhaseStartSeconds = Now;
			Phase = EPhase::PilotSettle;
		}
		return;
	}

	if (Phase == EPhase::PilotSettle)
	{
		MaybeLogDiagnostic(TEXT("pilot_settle"));
		if (++SettleFrames >= RequiredSettleFrames)
		{
			RequestCurrentScreenshot(true);
		}
		return;
	}

	if (Phase == EPhase::ViewSettle)
	{
		MaybeLogDiagnostic(TEXT("view_settle"));
		if (++SettleFrames >= RequiredSettleFrames)
		{
			RequestCurrentScreenshot(false);
		}
	}
}

bool USkyguardM01GroupedTopologyRecovery12Capture::IsWorldRenderable(
	FString& OutIssue) const
{
	const UWorld* World = GetWorld();
	if (!World || !World->HasBegunPlay())
	{
		OutIssue = TEXT("world_has_not_begun_play");
		return false;
	}
	if (World->GetOutermost()->GetName() != ExpectedMap)
	{
		OutIssue = FString::Printf(
			TEXT("loaded_map_mismatch:%s"),
			*World->GetOutermost()->GetName());
		return false;
	}
	if (!GEngine || !GEngine->GameViewport
		|| !GEngine->GameViewport->GetGameViewport())
	{
		OutIssue = TEXT("game_scene_viewport_unavailable");
		return false;
	}
	const FIntPoint LiveSize = GetLiveViewportSize();
	if (LiveSize.X <= 0 || LiveSize.Y <= 0)
	{
		OutIssue = FString::Printf(
			TEXT("live_viewport_has_no_renderable_extent:%s"),
			*LiveSize.ToString());
		return false;
	}
	if (!FApp::GetGraphicsRHI().Contains(TEXT("D3D12"))
		|| FString(LexToString(GMaxRHIFeatureLevel)) != TEXT("SM6"))
	{
		OutIssue = FString::Printf(
			TEXT("active_rhi_not_d3d12_sm6:%s|%s"),
			*FApp::GetGraphicsRHI(),
			*LexToString(GMaxRHIFeatureLevel));
		return false;
	}
	return true;
}

bool USkyguardM01GroupedTopologyRecovery12Capture::ConfigureScene()
{
	if (IFileManager::Get().DirectoryExists(*OutputRoot))
	{
		return false;
	}
	if (!IFileManager::Get().MakeDirectory(*OutputRoot, true)
		|| !IFileManager::Get().MakeDirectory(
			*FPaths::Combine(OutputRoot, TEXT("pilot")),
			true)
		|| !IFileManager::Get().MakeDirectory(
			*FPaths::Combine(OutputRoot, TEXT("full_views")),
			true))
	{
		return false;
	}

	UWorld* World = GetWorld();
	if (!World)
	{
		return false;
	}
	for (TActorIterator<AActor> It(World); It; ++It)
	{
#if WITH_EDITOR
		const FString Label = It->GetActorLabel();
#else
		const FString Label = It->GetName();
#endif
		if (!Label.StartsWith(TEXT("M01C008A03_"))
			|| Label.Contains(TEXT("Transient")))
		{
			continue;
		}
		for (const FString Family : {
			TEXT("Pathfinder"),
			TEXT("Lighthouse"),
			TEXT("RadarPost")})
		{
			if (Label.Contains(Family))
			{
				FamilyActors.FindOrAdd(Family).Add(*It);
				FVector Origin;
				FVector Extent;
				It->GetActorBounds(false, Origin, Extent, true);
				FamilyBounds.FindOrAdd(Family) +=
					FBox::BuildAABB(Origin, Extent);
			}
		}
	}
	for (const FString Family : {
		TEXT("Pathfinder"),
		TEXT("Lighthouse"),
		TEXT("RadarPost")})
	{
		if (FamilyActors.FindRef(Family).Num() != 4
			|| !FamilyBounds.FindRef(Family).IsValid)
		{
			return false;
		}
	}

	ADirectionalLight* Key = World->SpawnActor<ADirectionalLight>(
		FVector(3000.0, -2500.0, 7000.0),
		FRotator(-38.0, 42.0, 0.0));
	ADirectionalLight* Fill = World->SpawnActor<ADirectionalLight>(
		FVector(3000.0, 2500.0, 5000.0),
		FRotator(-18.0, -142.0, 0.0));
	ASkyLight* Sky = World->SpawnActor<ASkyLight>(
		FVector(3000.0, 0.0, 3000.0),
		FRotator::ZeroRotator);
	ASkyAtmosphere* Atmosphere = World->SpawnActor<ASkyAtmosphere>();
	Camera = World->SpawnActor<ACameraActor>();
	UDirectionalLightComponent* KeyComponent =
		Key
			? Cast<UDirectionalLightComponent>(Key->GetLightComponent())
			: nullptr;
	USkyLightComponent* SkyComponent =
		Sky ? Sky->GetLightComponent() : nullptr;
	if (!Key || !Fill || !Sky || !Atmosphere || !Camera
		|| !KeyComponent || !SkyComponent)
	{
		return false;
	}
	Key->GetLightComponent()->SetMobility(EComponentMobility::Movable);
	Fill->GetLightComponent()->SetMobility(EComponentMobility::Movable);
	SkyComponent->SetMobility(EComponentMobility::Movable);
	Key->GetLightComponent()->SetIntensity(100000.0f);
	Fill->GetLightComponent()->SetIntensity(12000.0f);
	SkyComponent->SetIntensity(2.25f);
	KeyComponent->SetAtmosphereSunLight(true);
	Camera->GetCameraComponent()->SetFieldOfView(45.0f);
	TransientActors = {Key, Fill, Sky, Atmosphere, Camera};

	APlayerController* Controller = World->GetFirstPlayerController();
	if (!Controller)
	{
		return false;
	}
	Controller->SetViewTarget(Camera);
	bSceneConfigured = true;
	return true;
}

bool USkyguardM01GroupedTopologyRecovery12Capture::ConfigureView(
	const FString& Family,
	const FString& View)
{
	if (!Camera || !FamilyActors.Contains(Family)
		|| !FamilyBounds.Contains(Family))
	{
		return false;
	}
	for (const TPair<FString, TArray<TObjectPtr<AActor>>>& Pair : FamilyActors)
	{
		for (AActor* Actor : Pair.Value)
		{
			Actor->SetActorHiddenInGame(Pair.Key != Family);
		}
	}
	const FBox Bounds = FamilyBounds.FindChecked(Family);
	const FVector Origin = Bounds.GetCenter();
	const FVector Extent = Bounds.GetExtent();
	const double Radius = FMath::Max3(
		FMath::Max(Extent.X, 100.0),
		Extent.Y,
		Extent.Z);
	const double Distance = Radius * 2.7;
	FVector Location;
	if (View == TEXT("three_quarter"))
	{
		Location = Origin
			+ FVector(-Distance * 0.72, -Distance * 0.72, Distance * 0.32);
	}
	else if (View == TEXT("grazing_port"))
	{
		Location = Origin + FVector(0.0, -Distance, Distance * 0.10);
	}
	else if (View == TEXT("grazing_starboard"))
	{
		Location = Origin + FVector(0.0, Distance, Distance * 0.10);
	}
	else
	{
		return false;
	}
	Camera->SetActorLocationAndRotation(
		Location,
		(Origin - Location).Rotation());
	PendingFamily = Family;
	PendingView = View;
	return true;
}

void USkyguardM01GroupedTopologyRecovery12Capture::
	RequestCurrentScreenshot(const bool bPilot)
{
	FSceneViewport* SceneViewport =
		GEngine && GEngine->GameViewport
			? GEngine->GameViewport->GetGameViewport()
			: nullptr;
	if (!SceneViewport)
	{
		Fail(TEXT("Game scene viewport disappeared before capture."));
		return;
	}
	bCurrentRequestPilot = bPilot;
	PendingPath = bPilot
		? FPaths::Combine(
			OutputRoot,
			TEXT("pilot"),
			FString::Printf(TEXT("Pilot_%02d.png"), PilotIndex))
		: FPaths::Combine(
			OutputRoot,
			TEXT("full_views"),
			FString::Printf(
				TEXT("%02d_%s_%s.png"),
				ViewIndex,
				*PendingFamily,
				*PendingView));

	FHighResScreenshotConfig& HighRes = GetHighResScreenshotConfig();
	HighRes.SetFilename(PendingPath);
	if (!HighRes.SetResolution(RequiredWidth, RequiredHeight, 1.0f))
	{
		Fail(TEXT("UE high-resolution configuration rejected 2048x2048."));
		return;
	}
	if (IFileManager::Get().FileExists(*PendingPath))
	{
		Fail(TEXT("Recovery12 output path already exists."));
		return;
	}
	PendingObservedFileSize = -1;
	PendingFileStableFrames = 0;
	bScreenshotPending = true;
	RequestStartSeconds = FPlatformTime::Seconds();
	Phase = bPilot
		? EPhase::PilotAwaitScreenshot
		: EPhase::ViewAwaitScreenshot;
	UE_LOG(
		LogSkyguardRecovery12,
		Display,
		TEXT(
			"[RECOVERY12][CAPTURE_REQUEST] family=%s view=%s "
			"output=2048x2048 live_viewport=%s"),
		*PendingFamily,
		*PendingView,
		*GetLiveViewportSize().ToString());
	if (!SceneViewport->TakeHighResScreenShot())
	{
		bScreenshotPending = false;
		Fail(TEXT("FViewport::TakeHighResScreenShot rejected the request."));
	}
}

void USkyguardM01GroupedTopologyRecovery12Capture::
	HandleScreenshotCaptured(
		const int32 Width,
		const int32 Height,
		const TArray<FColor>& Colors)
{
	CompleteCurrentCapture(
		Width,
		Height,
		TArrayView64<const FColor>(Colors.GetData(), Colors.Num()),
		TEXT("game_viewport_delegate"),
		true);
}

bool USkyguardM01GroupedTopologyRecovery12Capture::
	TryCompleteCurrentCaptureFromFilesystem()
{
	const int64 FileSize = IFileManager::Get().FileSize(*PendingPath);
	if (FileSize < MinimumPngBytes)
	{
		PendingObservedFileSize = FileSize;
		PendingFileStableFrames = 0;
		return false;
	}
	if (FileSize != PendingObservedFileSize)
	{
		PendingObservedFileSize = FileSize;
		PendingFileStableFrames = 1;
		return false;
	}
	++PendingFileStableFrames;
	if (PendingFileStableFrames < FilesystemStableFramesRequired)
	{
		return false;
	}
	TArray<uint8> PngBytes;
	if (!FFileHelper::LoadFileToArray(PngBytes, *PendingPath)
		|| PngBytes.Num() < 24
		|| PngBytes[0] != 0x89 || PngBytes[1] != 0x50
		|| PngBytes[2] != 0x4e || PngBytes[3] != 0x47
		|| PngBytes[12] != 0x49 || PngBytes[13] != 0x48
		|| PngBytes[14] != 0x44 || PngBytes[15] != 0x52)
	{
		Fail(TEXT("Stable screenshot file is not a valid PNG IHDR."));
		return true;
	}
	const int32 PngWidth =
		(static_cast<int32>(PngBytes[16]) << 24)
		| (static_cast<int32>(PngBytes[17]) << 16)
		| (static_cast<int32>(PngBytes[18]) << 8)
		| static_cast<int32>(PngBytes[19]);
	const int32 PngHeight =
		(static_cast<int32>(PngBytes[20]) << 24)
		| (static_cast<int32>(PngBytes[21]) << 16)
		| (static_cast<int32>(PngBytes[22]) << 8)
		| static_cast<int32>(PngBytes[23]);
	FSceneViewport* SceneViewport =
		GEngine && GEngine->GameViewport
			? GEngine->GameViewport->GetGameViewport()
			: nullptr;
	TArray<FColor> Colors;
	if (!SceneViewport || !SceneViewport->ReadPixels(Colors))
	{
		Fail(TEXT("Stable PNG fallback live readback failed."));
		return true;
	}
	const FIntPoint LiveSize = SceneViewport->GetSizeXY();
	if (PngWidth != RequiredWidth || PngHeight != RequiredHeight
		|| LiveSize.X != PngWidth || LiveSize.Y != PngHeight
		|| Colors.Num() != PngWidth * PngHeight)
	{
		Fail(TEXT("Stable PNG and live readback dimensions differ."));
		return true;
	}
	CompleteCurrentCapture(
		PngWidth,
		PngHeight,
		TArrayView64<const FColor>(Colors.GetData(), Colors.Num()),
		TEXT("stable_filesystem_png_plus_live_readback"),
		false);
	return true;
}

void USkyguardM01GroupedTopologyRecovery12Capture::
	CompleteCurrentCapture(
		const int32 Width,
		const int32 Height,
		const TArrayView64<const FColor> Colors,
		const FString& CompletionMethod,
		const bool bPersistPng)
{
	if (!bScreenshotPending)
	{
		return;
	}
	bScreenshotPending = false;
	GetHighResScreenshotConfig().SetFilename(FString());
	FCaptureRecord Record = BuildRecord(Width, Height, Colors);
	Record.Family = PendingFamily;
	Record.View = PendingView;
	Record.Path = PendingPath;
	Record.CompletionMethod = CompletionMethod;
	UE_LOG(
		LogSkyguardRecovery12,
		Display,
		TEXT(
			"[RECOVERY12][CAPTURE_COMPLETE] method=%s "
			"family=%s view=%s pixels=%dx%d live=%s "
			"hard_bounds=%s"),
		*CompletionMethod,
		*PendingFamily,
		*PendingView,
		Width,
		Height,
		*GetLiveViewportSize().ToString(),
		Record.bHardBoundsPassed ? TEXT("true") : TEXT("false"));
	if (Width != RequiredWidth || Height != RequiredHeight)
	{
		Fail(FString::Printf(
			TEXT(
				"High-resolution callback dimension mismatch: "
				"expected=2048x2048 actual=%dx%d"),
			Width,
			Height));
		return;
	}
	if (bPersistPng && !WritePng(PendingPath, Width, Height, Colors))
	{
		Fail(TEXT("Could not persist Recovery12 high-resolution PNG."));
		return;
	}

	if (bCurrentRequestPilot)
	{
		PilotRecords.Add(Record);
		if (!Record.bLivenessPassed)
		{
			Fail(TEXT("Recovery12 high-resolution pilot was not live."));
			return;
		}
		++PilotIndex;
		if (PilotIndex < 3)
		{
			SettleFrames = 0;
			PhaseStartSeconds = FPlatformTime::Seconds();
			Phase = EPhase::PilotSettle;
			return;
		}
		if (!ConfigureView(
			GovernedViews[0].Key,
			GovernedViews[0].Value))
		{
			Fail(TEXT("Could not configure first governed view."));
			return;
		}
		SettleFrames = 0;
		PhaseStartSeconds = FPlatformTime::Seconds();
		Phase = EPhase::ViewSettle;
		return;
	}

	ViewRecords.Add(Record);
	++ViewIndex;
	if (ViewIndex >= GovernedViews.Num())
	{
		Finish();
		return;
	}
	if (!ConfigureView(
		GovernedViews[ViewIndex].Key,
		GovernedViews[ViewIndex].Value))
	{
		Fail(TEXT("Could not configure governed view."));
		return;
	}
	SettleFrames = 0;
	PhaseStartSeconds = FPlatformTime::Seconds();
	Phase = EPhase::ViewSettle;
}

USkyguardM01GroupedTopologyRecovery12Capture::FCaptureRecord
USkyguardM01GroupedTopologyRecovery12Capture::BuildRecord(
	const int32 Width,
	const int32 Height,
	const TArrayView64<const FColor> Colors) const
{
	FCaptureRecord Record;
	Record.Width = Width;
	Record.Height = Height;
	TArray<int64> Histogram;
	Histogram.Init(0, 256);
	TSet<uint32> UniqueColors;
	int32 MaximumChannel = 0;
	for (const FColor& Color : Colors)
	{
		const uint8 Luma = static_cast<uint8>(
			(54 * Color.R + 183 * Color.G + 19 * Color.B) / 256);
		if (Luma > ActiveThreshold)
		{
			++Histogram[Luma];
		}
		MaximumChannel = FMath::Max3(
			MaximumChannel,
			static_cast<int32>(Color.R),
			FMath::Max(
				static_cast<int32>(Color.G),
				static_cast<int32>(Color.B)));
		if (UniqueColors.Num() < 4096)
		{
			UniqueColors.Add(Color.ToPackedARGB());
		}
	}
	int64 Active = 0;
	int64 Clipped = 0;
	for (int32 Value = 0; Value < 256; ++Value)
	{
		Active += Histogram[Value];
		if (Value >= 250)
		{
			Clipped += Histogram[Value];
		}
	}
	Record.ActivePixelFraction = Colors.IsEmpty()
		? 0.0
		: static_cast<double>(Active) / Colors.Num();
	Record.ActiveClippedFraction = Active == 0
		? 1.0
		: static_cast<double>(Clipped) / Active;
	Record.ActiveP05 = HistogramPercentile(Histogram, 0.05);
	Record.ActiveP50 = HistogramPercentile(Histogram, 0.50);
	Record.ActiveP95 = HistogramPercentile(Histogram, 0.95);
	Record.ActiveDynamicRange = Record.ActiveP95 - Record.ActiveP05;
	Record.MaximumChannel = MaximumChannel;
	Record.UniqueColorCount = UniqueColors.Num();
	Record.bLivenessPassed =
		Width == RequiredWidth
		&& Height == RequiredHeight
		&& Record.ActivePixelFraction >= MinimumActiveFraction
		&& Record.MaximumChannel >= MinimumMaximumChannel
		&& Record.UniqueColorCount >= MinimumUniqueColors;
	Record.bHardBoundsPassed =
		Record.bLivenessPassed
		&& Record.ActiveClippedFraction <= MaximumClippedFraction
		&& Record.ActiveP50 >= MinimumP50
		&& Record.ActiveP50 <= MaximumP50
		&& Record.ActiveP95 >= MinimumP95
		&& Record.ActiveP95 <= MaximumP95
		&& Record.ActiveDynamicRange >= MinimumDynamicRange;
	return Record;
}

bool USkyguardM01GroupedTopologyRecovery12Capture::WritePng(
	const FString& Path,
	const int32 Width,
	const int32 Height,
	const TArrayView64<const FColor> Colors) const
{
	TArray64<uint8> Compressed;
	FImageUtils::PNGCompressImageArray(
		Width,
		Height,
		Colors,
		Compressed);
	return Compressed.Num() > 25000
		&& FFileHelper::SaveArrayToFile(Compressed, *Path);
}

bool USkyguardM01GroupedTopologyRecovery12Capture::WriteReceipt(
	const FString& Gate,
	const FString& Issue) const
{
	const TSharedRef<FJsonObject> Receipt = MakeShared<FJsonObject>();
	Receipt->SetStringField(
		TEXT("schema"),
		TEXT(
			"skyguard.m01.hero-grouped-topology-"
			"recovery12-highres-capture.v1"));
	Receipt->SetStringField(TEXT("contract_id"), ContractId);
	Receipt->SetStringField(TEXT("gate"), Gate);
	Receipt->SetStringField(TEXT("issue"), Issue);
	Receipt->SetStringField(TEXT("phase"), PhaseName());
	Receipt->SetStringField(TEXT("last_readiness_issue"), LastReadinessIssue);
	Receipt->SetStringField(TEXT("map"), ExpectedMap);
	Receipt->SetStringField(TEXT("rhi"), FApp::GetGraphicsRHI());
	Receipt->SetStringField(
		TEXT("feature_level"),
		LexToString(GMaxRHIFeatureLevel));
	Receipt->SetStringField(
		TEXT("capture_resolution_path"),
		TEXT(
			"FHighResScreenshotConfig::SetResolution+"
			"FViewport::TakeHighResScreenShot+"
			"UGameViewportClient::OnScreenshotCaptured"));
	Receipt->SetStringField(
		TEXT("completion_fallback"),
		TEXT("stable_filesystem_png_plus_live_readback"));
	const FIntPoint LiveSize = GetLiveViewportSize();
	Receipt->SetNumberField(TEXT("live_viewport_width"), LiveSize.X);
	Receipt->SetNumberField(TEXT("live_viewport_height"), LiveSize.Y);
	Receipt->SetNumberField(TEXT("required_output_width"), RequiredWidth);
	Receipt->SetNumberField(TEXT("required_output_height"), RequiredHeight);
	Receipt->SetBoolField(
		TEXT("live_viewport_resolution_independent"),
		true);
	Receipt->SetBoolField(TEXT("native_frame_driven_capture"), true);
	Receipt->SetBoolField(TEXT("python_scene_capture_used"), false);
	Receipt->SetNumberField(
		TEXT("world_readiness_timeout_seconds"),
		WorldReadinessTimeoutSeconds);
	Receipt->SetNumberField(
		TEXT("screenshot_timeout_seconds"),
		ScreenshotTimeoutSeconds);
	Receipt->SetNumberField(
		TEXT("absolute_session_timeout_seconds"),
		AbsoluteSessionTimeoutSeconds);
	Receipt->SetNumberField(
		TEXT("elapsed_seconds"),
		FPlatformTime::Seconds() - SessionStartSeconds);
	Receipt->SetNumberField(
		TEXT("consecutive_ready_frames"),
		ConsecutiveReadyFrames);
	Receipt->SetNumberField(TEXT("warmup_frames"), WarmupFrames);
	Receipt->SetNumberField(TEXT("pilot_capture_count"), PilotRecords.Num());
	Receipt->SetNumberField(TEXT("full_view_capture_count"), ViewRecords.Num());
	TArray<TSharedPtr<FJsonValue>> PilotJson;
	for (const FCaptureRecord& Record : PilotRecords)
	{
		PilotJson.Add(MakeShared<FJsonValueObject>(RecordToJson(Record)));
	}
	Receipt->SetArrayField(TEXT("pilot_captures"), PilotJson);
	TArray<TSharedPtr<FJsonValue>> ViewJson;
	for (const FCaptureRecord& Record : ViewRecords)
	{
		ViewJson.Add(MakeShared<FJsonValueObject>(RecordToJson(Record)));
	}
	Receipt->SetArrayField(TEXT("full_view_captures"), ViewJson);
	Receipt->SetBoolField(TEXT("world_saved"), false);
	Receipt->SetBoolField(TEXT("package_save_invoked"), false);
	Receipt->SetBoolField(TEXT("promotion_allowed"), false);
	Receipt->SetBoolField(TEXT("p3_4_closed"), false);
	Receipt->SetStringField(
		TEXT("completed_at_utc"),
		FDateTime::UtcNow().ToIso8601());
	FString Json;
	const TSharedRef<TJsonWriter<>> Writer =
		TJsonWriterFactory<>::Create(&Json);
	return FJsonSerializer::Serialize(Receipt, Writer)
		&& FFileHelper::SaveStringToFile(
			Json,
			*FPaths::Combine(OutputRoot, TEXT("capture_receipt.json")),
			FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}

void USkyguardM01GroupedTopologyRecovery12Capture::MaybeLogDiagnostic(
	const FString& Issue)
{
	const double Now = FPlatformTime::Seconds();
	if (Now - LastDiagnosticSeconds < DiagnosticIntervalSeconds)
	{
		return;
	}
	LastDiagnosticSeconds = Now;
	const FIntPoint LiveSize = GetLiveViewportSize();
	UE_LOG(
		LogSkyguardRecovery12,
		Display,
		TEXT(
			"[RECOVERY12][STATE] phase=%s elapsed=%.2f "
			"phase_elapsed=%.2f live_viewport=%dx%d issue=%s"),
		*PhaseName(),
		Now - SessionStartSeconds,
		Now - PhaseStartSeconds,
		LiveSize.X,
		LiveSize.Y,
		*Issue);
}

FIntPoint
USkyguardM01GroupedTopologyRecovery12Capture::GetLiveViewportSize() const
{
	const FSceneViewport* SceneViewport =
		GEngine && GEngine->GameViewport
			? GEngine->GameViewport->GetGameViewport()
			: nullptr;
	return SceneViewport
		? SceneViewport->GetSizeXY()
		: FIntPoint::ZeroValue;
}

FString USkyguardM01GroupedTopologyRecovery12Capture::PhaseName() const
{
	switch (Phase)
	{
	case EPhase::WaitForWorld:
		return TEXT("WaitForWorld");
	case EPhase::Warmup:
		return TEXT("Warmup");
	case EPhase::PilotSettle:
		return TEXT("PilotSettle");
	case EPhase::PilotAwaitScreenshot:
		return TEXT("PilotAwaitScreenshot");
	case EPhase::ViewSettle:
		return TEXT("ViewSettle");
	case EPhase::ViewAwaitScreenshot:
		return TEXT("ViewAwaitScreenshot");
	case EPhase::Finished:
		return TEXT("Finished");
	case EPhase::Failed:
		return TEXT("Failed");
	default:
		return TEXT("Unknown");
	}
}

void USkyguardM01GroupedTopologyRecovery12Capture::Fail(
	const FString& Issue)
{
	const FString FailedPhase = PhaseName();
	Phase = EPhase::Failed;
	IFileManager::Get().MakeDirectory(*OutputRoot, true);
	UE_LOG(
		LogSkyguardRecovery12,
		Error,
		TEXT("[RECOVERY12][FAIL] phase=%s issue=%s"),
		*FailedPhase,
		*Issue);
	WriteReceipt(TEXT("FAIL_CLOSED_RECOVERY12_HIGHRES_CAPTURE"), Issue);
	FPlatformMisc::RequestExitWithStatus(
		false,
		3,
		TEXT("SkyguardM01Recovery12HighResCaptureFailed"));
}

void USkyguardM01GroupedTopologyRecovery12Capture::Finish()
{
	const bool bPilotLive =
		PilotRecords.Num() == 3
		&& Algo::AllOf(
			PilotRecords,
			[](const FCaptureRecord& Record)
			{
				return Record.bLivenessPassed;
			});
	const bool bViewsPass =
		ViewRecords.Num() == 9
		&& Algo::AllOf(
			ViewRecords,
			[](const FCaptureRecord& Record)
			{
				return Record.bHardBoundsPassed;
			});
	const bool bPass = bPilotLive && bViewsPass;
	WriteReceipt(
		bPass
			? TEXT(
				"PASS_RECOVERY12_HIGHRES_CAPTURE_"
				"AWAITING_OFFLINE_AUDIT")
			: TEXT("FAIL_CLOSED_RECOVERY12_HIGHRES_VIEW_BOUNDS"),
		bPass ? FString() : TEXT("Pilot or governed view bounds failed."));
	Phase = bPass ? EPhase::Finished : EPhase::Failed;
	UE_LOG(
		LogSkyguardRecovery12,
		Display,
		TEXT(
			"[RECOVERY12][COMPLETE] pass=%s pilot=%d views=%d"),
		bPass ? TEXT("true") : TEXT("false"),
		PilotRecords.Num(),
		ViewRecords.Num());
	FPlatformMisc::RequestExitWithStatus(
		false,
		bPass ? 0 : 3,
		TEXT("SkyguardM01Recovery12HighResCaptureComplete"));
}

void USkyguardM01GroupedTopologyRecovery12Capture::
	RestoreScreenshotDelegateCVar()
{
	if (!bScreenshotDelegateCVarCaptured)
	{
		return;
	}
	if (IConsoleVariable* ScreenshotDelegateCVar =
		IConsoleManager::Get().FindConsoleVariable(
			TEXT("r.ScreenshotDelegate")))
	{
		ScreenshotDelegateCVar->Set(
			PreviousScreenshotDelegateValue,
			ECVF_SetByCode);
	}
	bScreenshotDelegateCVarCaptured = false;
}

void USkyguardM01GroupedTopologyRecovery12Capture::RestoreVisibility()
{
	for (const TPair<FString, TArray<TObjectPtr<AActor>>>& Pair : FamilyActors)
	{
		for (AActor* Actor : Pair.Value)
		{
			if (Actor)
			{
				Actor->SetActorHiddenInGame(false);
			}
		}
	}
	for (AActor* Actor : TransientActors)
	{
		if (Actor)
		{
			Actor->Destroy();
		}
	}
	TransientActors.Reset();
	FamilyActors.Reset();
	FamilyBounds.Reset();
	Camera = nullptr;
	bSceneConfigured = false;
}
