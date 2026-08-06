#include "SkyguardRecovery03NativeRecovery05Module.h"

#include "AssetCompilingManager.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Dom/JsonObject.h"
#include "DynamicRHI.h"
#include "Editor.h"
#include "Engine/SceneCapture2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GenericPlatform/GenericPlatformMisc.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformMemory.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "Kismet/KismetRenderingLibrary.h"
#include "LandscapeComponent.h"
#include "LandscapeProxy.h"
#include "MaterialShared.h"
#include "Materials/MaterialInstance.h"
#include "Materials/MaterialInterface.h"
#include "Misc/App.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "RHI.h"
#include "RHIStats.h"
#include "RenderingThread.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "ShaderCompiler.h"
#include "UnrealEdGlobals.h"
#include "Editor/UnrealEdEngine.h"

namespace
{
constexpr TCHAR RequiredContractId[] =
    TEXT("P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03-NATIVE-BUILD-RECOVERY-01");
constexpr TCHAR RequiredAuthorization[] =
    TEXT("P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-03-NATIVE-BUILD-RECOVERY-01-ONE-SHOT");
constexpr TCHAR RequiredAttemptSuffix[] =
    TEXT("Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01/runtime_attempt_01");
constexpr TCHAR RequiredMap[] =
    TEXT("/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03");
constexpr TCHAR RequiredLandscapeLabel[] = TEXT("M01_P4_Landscape_Production");
constexpr TCHAR RequiredMaterial[] =
    TEXT("/Game/Skyguard/Materials/Mission01/LandscapeValidation_v6_attempt06/M_M01_Landscape_Validation_v6_attempt06");
constexpr int32 RequiredComponents = 16;
constexpr int32 RequiredStablePolls = 2;
constexpr int32 RequiredFrames = 900;
constexpr int32 RequiredCaptures = 8;
constexpr int32 CaptureWidth = 2560;
constexpr int32 CaptureHeight = 1440;
constexpr double WarmupSeconds = 30.0;
constexpr double MeasureSeconds = 30.0;
constexpr double MaximumSeconds = 480.0;

struct FImmutableRecord
{
    const TCHAR* RelativeFile;
    int64 Bytes;
    const TCHAR* Sha256;
};

const FImmutableRecord ImmutableRecords[] = {
    {TEXT("Content/Skyguard/Maps/Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03.umap"), 532796,
     TEXT("447e7ac49dc6c843f33bfc177ff46134b10035b6c6765d354ef790acf7f58d72")},
    {TEXT("Content/Skyguard/Materials/Mission01/LandscapeValidation_v6_attempt06/M_M01_Landscape_Validation_v6_attempt06.uasset"), 15059,
     TEXT("28e887486a82a146efe9fe02478851b940b151e40bd02849f2a9709e9b0220b2")},
    {TEXT("Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_CAMERAS.json"), 2651,
     TEXT("2f54ab9c9a8338ca344e67a00261f715715e2fb3ab4c7adb341c59ee2a0a5a94")},
    {TEXT("Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_VISUAL_RUBRIC.json"), 1986,
     TEXT("43044af006f13beb267146adea6f465872ed31133df36fdf5c41f538201cec59")},
    {TEXT("Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_PERFORMANCE_RUBRIC.json"), 1332,
     TEXT("2c4476d02c87ba84cbdbd6bb69de534cec4fdf04f376589e07678074b372e644")},
    {TEXT("Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY03_NATIVE_BUILD_RECOVERY01_CONTRACT.json"), 3016,
     TEXT("3e66b5005d5ca995039fd6d96a3b9553960a91d8b017261f2ecd99d89e85afac")}
};

const FSkyguardRecovery03NativeRecovery05Module::FCaptureSpec CaptureSpecs[] = {
    {TEXT("C01_REAR_GUNNER_PORT"), FVector(22500, 3000, 1100), FRotator(-6, 112, 0), 1},
    {TEXT("C02_REAR_GUNNER_STARBOARD"), FVector(22500, 3000, 1100), FRotator(-5, 68, 0), 1},
    {TEXT("C03_SHORELINE_APPROACH"), FVector(22500, 3000, 900), FRotator(-6, 90, 0), 1},
    {TEXT("C04_ROUTE_EXTERIOR"), FVector(22500, -9000, 8500), FRotator(-28, 90, 0), 1},
    {TEXT("C05_CITY_INLAND"), FVector(22500, 9600, 800), FRotator(-12, 25, 0), 1},
    {TEXT("T01_ROUTE_ENTRY"), FVector(22500, 2400, 1050), FRotator(-5, 92, 0), 15},
    {TEXT("T02_ROUTE_MID"), FVector(22500, 3000, 1050), FRotator(-5, 92, 0), 15},
    {TEXT("T03_ROUTE_EXIT"), FVector(22500, 3600, 1050), FRotator(-5, 92, 0), 15}
};

bool SaveJson(const FString& File, const TSharedRef<FJsonObject>& Object)
{
    FString Text;
    const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Text);
    return FJsonSerializer::Serialize(Object, Writer)
        && FFileHelper::SaveStringToFile(
            Text + TEXT("\n"), *File,
            FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}
}

void FSkyguardRecovery03NativeRecovery05Module::StartupModule()
{
    bAuthorized = ParseAuthorization();
    if (!bAuthorized)
    {
        Phase = EPhase::Inert;
        return;
    }
    StartedSeconds = FPlatformTime::Seconds();
    PhaseStartedSeconds = StartedSeconds;
    Phase = EPhase::Preflight;
    TickerHandle = FTSTicker::GetCoreTicker().AddTicker(
        FTickerDelegate::CreateRaw(this, &FSkyguardRecovery03NativeRecovery05Module::Tick));
}

void FSkyguardRecovery03NativeRecovery05Module::ShutdownModule()
{
    if (TickerHandle.IsValid())
    {
        FTSTicker::GetCoreTicker().RemoveTicker(TickerHandle);
    }
    if (bAuthorized && !bTerminalReceiptWritten)
    {
        CompleteTerminal(false, TEXT("Editor shutdown occurred before terminal receipt."), 19);
    }
}

bool FSkyguardRecovery03NativeRecovery05Module::ParseAuthorization()
{
    FParse::Value(FCommandLine::Get(), TEXT("SkyguardRecovery01ContractId="), ContractId);
    FParse::Value(FCommandLine::Get(), TEXT("SkyguardRecovery01Authorization="), AuthorizationToken);
    FParse::Value(FCommandLine::Get(), TEXT("SkyguardRecovery01ExpectedMap="), ExpectedMap);
    FParse::Value(FCommandLine::Get(), TEXT("SkyguardRecovery01AttemptRoot="), AttemptRoot);
    FPaths::NormalizeDirectoryName(AttemptRoot);
    FString ExpectedSuffix = RequiredAttemptSuffix;
    ExpectedSuffix.ReplaceInline(TEXT("/"), TEXT("\\"));
    return ContractId == RequiredContractId
        && AuthorizationToken == RequiredAuthorization
        && ExpectedMap == RequiredMap
        && AttemptRoot.EndsWith(ExpectedSuffix, ESearchCase::CaseSensitive)
        && !IFileManager::Get().DirectoryExists(*AttemptRoot);
}

FString FSkyguardRecovery03NativeRecovery05Module::HashFile(const FString& File) const
{
    TArray<uint8> Data;
    if (!FFileHelper::LoadFileToArray(Data, *File)
        || Data.Num() > static_cast<int64>(MAX_uint32))
    {
        return FString();
    }
    FSHA256Signature Signature{};
    if (!FPlatformMisc::GetSHA256Signature(
        Data.GetData(), static_cast<uint32>(Data.Num()), Signature))
    {
        return FString();
    }
    return Signature.ToString().ToLower();
}

bool FSkyguardRecovery03NativeRecovery05Module::VerifyFile(
    const FString& File, int64 Bytes, const FString& Sha256, FString& OutIssue) const
{
    const int64 ActualBytes = IFileManager::Get().FileSize(*File);
    if (ActualBytes != Bytes)
    {
        OutIssue = FString::Printf(TEXT("Immutable byte mismatch: %s"), *File);
        return false;
    }
    if (HashFile(File) != Sha256)
    {
        OutIssue = FString::Printf(TEXT("Immutable SHA-256 mismatch: %s"), *File);
        return false;
    }
    return true;
}

bool FSkyguardRecovery03NativeRecovery05Module::VerifyImmutableInputs(FString& OutIssue) const
{
    for (const FImmutableRecord& Record : ImmutableRecords)
    {
        if (!VerifyFile(
            FPaths::ConvertRelativePathToFull(FPaths::ProjectDir(), Record.RelativeFile),
            Record.Bytes, Record.Sha256, OutIssue))
        {
            return false;
        }
    }
    return true;
}

bool FSkyguardRecovery03NativeRecovery05Module::VerifyWorldAndAssets(FString& OutIssue)
{
    if (!FApp::GetGraphicsRHI().Contains(TEXT("D3D12"))
        || FString(LexToString(GMaxRHIFeatureLevel)) != TEXT("SM6"))
    {
        OutIssue = TEXT("Active renderer is not D3D12 SM6.");
        return false;
    }
    if (!GEditor)
    {
        OutIssue = TEXT("Editor engine is unavailable.");
        return false;
    }
    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (!World || World->GetOutermost()->GetName() != ExpectedMap)
    {
        OutIssue = TEXT("Loaded editor world is not the exact governed map.");
        return false;
    }
    TArray<ALandscapeProxy*> Matches;
    for (TActorIterator<ALandscapeProxy> It(World); It; ++It)
    {
        if (It->GetActorLabel() == RequiredLandscapeLabel)
        {
            Matches.Add(*It);
        }
    }
    if (Matches.Num() != 1 || Matches[0]->LandscapeComponents.Num() != RequiredComponents)
    {
        OutIssue = TEXT("Governed landscape count or component count is not exact.");
        return false;
    }
    UMaterialInterface* Material = LoadObject<UMaterialInterface>(nullptr, RequiredMaterial);
    if (!Material)
    {
        OutIssue = TEXT("Validation material did not resolve.");
        return false;
    }
    Landscape = Matches[0];
    ValidationMaterial = Material;
    return true;
}

bool FSkyguardRecovery03NativeRecovery05Module::CreateFreshOutput(FString& OutIssue)
{
    if (IFileManager::Get().DirectoryExists(*AttemptRoot))
    {
        OutIssue = TEXT("Governed runtime namespace already exists.");
        return false;
    }
    ProofRoot = FPaths::Combine(AttemptRoot, TEXT("proof"));
    CaptureRoot = FPaths::Combine(ProofRoot, TEXT("captures"));
    if (!IFileManager::Get().MakeDirectory(*CaptureRoot, true))
    {
        OutIssue = TEXT("Could not create governed output directories.");
        return false;
    }
    return true;
}

FString FSkyguardRecovery03NativeRecovery05Module::MaterialIdentity(UMaterialInterface* Material) const
{
    return Material ? Material->GetPathName() : TEXT("<null>");
}

bool FSkyguardRecovery03NativeRecovery05Module::BindTransientMaterial(FString& OutIssue)
{
    ALandscapeProxy* Target = Landscape.Get();
    UMaterialInterface* Bound = ValidationMaterial.Get();
    if (!Target || !Bound)
    {
        OutIssue = TEXT("Landscape or validation material expired before binding.");
        return false;
    }
    OriginalMaterial = Target->LandscapeMaterial;
    OriginalMaterialIdentity = MaterialIdentity(OriginalMaterial.Get());
    Target->LandscapeMaterial = Bound;
    Target->UpdateAllComponentMaterialInstances(true);
    bMaterialBound = true;
    if (Target->LandscapeMaterial != Bound)
    {
        OutIssue = TEXT("Transient landscape material is not exact and non-null.");
        return false;
    }
    return true;
}

bool FSkyguardRecovery03NativeRecovery05Module::IsShaderReady(
    FString& OutIssue, int32& OutFinishedResources, int32& OutValidShaderMaps) const
{
    OutFinishedResources = 0;
    OutValidShaderMaps = 0;
    ALandscapeProxy* Target = Landscape.Get();
    if (!Target || Target->LandscapeComponents.Num() != RequiredComponents)
    {
        OutIssue = TEXT("Landscape component set changed.");
        return false;
    }
    if ((GShaderCompilingManager && GShaderCompilingManager->IsCompiling())
        || FAssetCompilingManager::Get().GetNumRemainingAssets() != 0)
    {
        OutIssue = TEXT("Compilation queues are active.");
        return false;
    }
    UWorld* World = Target->GetWorld();
    if (!World)
    {
        OutIssue = TEXT("Landscape world is unavailable.");
        return false;
    }
    const EShaderPlatform ShaderPlatform =
        GetFeatureLevelShaderPlatform_Checked(World->GetFeatureLevel());
    for (ULandscapeComponent* Component : Target->LandscapeComponents)
    {
        UMaterialInstance* Instance = Component ? Component->GetMaterialInstance(0, false) : nullptr;
        FMaterialResource* Resource = Instance ? Instance->GetMaterialResource(ShaderPlatform) : nullptr;
        if (Resource && Resource->IsCompilationFinished())
        {
            ++OutFinishedResources;
        }
        if (Resource && Resource->GetGameThreadShaderMap())
        {
            ++OutValidShaderMaps;
        }
    }
    return OutFinishedResources == RequiredComponents
        && OutValidShaderMaps == RequiredComponents;
}

void FSkyguardRecovery03NativeRecovery05Module::AppendHeartbeat(const FString& Event)
{
    if (AttemptRoot.IsEmpty() || !IFileManager::Get().DirectoryExists(*AttemptRoot))
    {
        return;
    }
    const FString Line = FString::Printf(
        TEXT("{\"tick\":%lld,\"phase\":%d,\"event\":\"%s\",\"seconds\":%.6f}\n"),
        TickOrdinal, static_cast<int32>(Phase), *Event, FPlatformTime::Seconds());
    FFileHelper::SaveStringToFile(
        Line, *FPaths::Combine(AttemptRoot, TEXT("lifecycle_heartbeat.jsonl")),
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,
        &IFileManager::Get(), FILEWRITE_Append);
}

bool FSkyguardRecovery03NativeRecovery05Module::VerifyPng(
    const FString& File, FString& OutIssue, int64& OutBytes, FString& OutHash) const
{
    TArray<uint8> Header;
    if (!FFileHelper::LoadFileToArray(Header, *File) || Header.Num() < 24)
    {
        OutIssue = TEXT("Capture file is absent or too small.");
        return false;
    }
    const uint8 Signature[8] = {137, 80, 78, 71, 13, 10, 26, 10};
    if (FMemory::Memcmp(Header.GetData(), Signature, 8) != 0)
    {
        OutIssue = TEXT("Capture is not a PNG.");
        return false;
    }
    auto ReadBE32 = [&Header](int32 Offset)
    {
        return (static_cast<uint32>(Header[Offset]) << 24)
            | (static_cast<uint32>(Header[Offset + 1]) << 16)
            | (static_cast<uint32>(Header[Offset + 2]) << 8)
            | static_cast<uint32>(Header[Offset + 3]);
    };
    if (ReadBE32(16) != CaptureWidth || ReadBE32(20) != CaptureHeight)
    {
        OutIssue = TEXT("Capture dimensions are not 2560x1440.");
        return false;
    }
    OutBytes = IFileManager::Get().FileSize(*File);
    OutHash = HashFile(File);
    return OutBytes > 0 && !OutHash.IsEmpty();
}

bool FSkyguardRecovery03NativeRecovery05Module::CaptureCurrent(FString& OutIssue)
{
    if (!CaptureSpecs[CaptureIndex].Id || !GEditor)
    {
        OutIssue = TEXT("Capture specification or editor is unavailable.");
        return false;
    }
    UWorld* World = GEditor->GetEditorWorldContext().World();
    ASceneCapture2D* Actor = World ? World->SpawnActor<ASceneCapture2D>() : nullptr;
    UTextureRenderTarget2D* Target = NewObject<UTextureRenderTarget2D>(GetTransientPackage());
    if (!World || !Actor || !Target)
    {
        if (Actor) { Actor->Destroy(); }
        OutIssue = TEXT("Could not allocate transient capture objects.");
        return false;
    }
    Target->AddToRoot();
    Target->ClearColor = FLinearColor::Black;
    Target->InitCustomFormat(CaptureWidth, CaptureHeight, PF_B8G8R8A8, true);
    Target->UpdateResourceImmediate(true);
    USceneCaptureComponent2D* Component = Actor->GetCaptureComponent2D();
    Component->TextureTarget = Target;
    Component->CaptureSource = ESceneCaptureSource::SCS_FinalColorLDR;
    Component->bCaptureEveryFrame = false;
    Component->bCaptureOnMovement = false;
    Component->FOVAngle = 90.0f;
    Actor->SetActorLocationAndRotation(
        CaptureSpecs[CaptureIndex].Location,
        CaptureSpecs[CaptureIndex].Rotation);
    Component->CaptureScene();
    FlushRenderingCommands();
    const FString Name = FString(CaptureSpecs[CaptureIndex].Id) + TEXT(".png");
    UKismetRenderingLibrary::ExportRenderTarget(World, Target, CaptureRoot, Name);
    Actor->Destroy();
    Target->RemoveFromRoot();
    const FString File = FPaths::Combine(CaptureRoot, Name);
    FCaptureRecord Record;
    Record.Id = CaptureSpecs[CaptureIndex].Id;
    Record.File = File;
    Record.Tick = TickOrdinal;
    if (!VerifyPng(File, OutIssue, Record.Bytes, Record.Sha256))
    {
        return false;
    }
    Captures.Add(MoveTemp(Record));
    AppendHeartbeat(FString::Printf(TEXT("capture_%d"), CaptureIndex));
    return true;
}

bool FSkyguardRecovery03NativeRecovery05Module::RestoreMaterial(FString& OutIssue)
{
    if (!bMaterialBound)
    {
        bRestorationVerified = true;
        RestoredMaterialIdentity = OriginalMaterialIdentity;
        return true;
    }
    ALandscapeProxy* Target = Landscape.Get();
    if (!Target)
    {
        OutIssue = TEXT("Landscape expired before restoration.");
        return false;
    }
    Target->LandscapeMaterial = OriginalMaterial.Get();
    Target->UpdateAllComponentMaterialInstances(true);
    RestoredMaterialIdentity = MaterialIdentity(Target->LandscapeMaterial);
    bRestorationVerified = RestoredMaterialIdentity == OriginalMaterialIdentity;
    bMaterialBound = !bRestorationVerified;
    if (!bRestorationVerified)
    {
        OutIssue = TEXT("Restored material identity differs from original identity.");
    }
    return bRestorationVerified;
}

void FSkyguardRecovery03NativeRecovery05Module::WriteFrameSamples() const
{
    FString Csv = TEXT("sample,frame_ms,gpu_ms,working_set_bytes,texture_memory_bytes,total_gpu_memory_bytes,available_texture_memory_bytes\n");
    for (int32 Index = 0; Index < FrameMilliseconds.Num(); ++Index)
    {
        Csv += FString::Printf(
            TEXT("%d,%.6f,%.6f,%llu,%llu,%lld,%lld\n"), Index,
            FrameMilliseconds[Index], GpuMilliseconds[Index],
            WorkingSetBytes[Index], TextureMemoryBytes[Index],
            TotalGpuMemoryBytes[Index], AvailableTextureMemoryBytes[Index]);
    }
    FFileHelper::SaveStringToFile(
        Csv, *FPaths::Combine(ProofRoot, TEXT("frame_samples.csv")),
        FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}

void FSkyguardRecovery03NativeRecovery05Module::WriteCaptureReceipt(
    bool bPassed, const FString& Issue) const
{
    const TSharedRef<FJsonObject> Root = MakeShared<FJsonObject>();
    Root->SetStringField(TEXT("contract_id"), ContractId);
    Root->SetBoolField(TEXT("passed"), bPassed);
    Root->SetStringField(TEXT("issue"), Issue);
    Root->SetNumberField(TEXT("capture_count"), Captures.Num());
    Root->SetNumberField(TEXT("frame_sample_count"), FrameMilliseconds.Num());
    Root->SetBoolField(TEXT("world_saved"), false);
    TArray<TSharedPtr<FJsonValue>> Values;
    for (const FCaptureRecord& Record : Captures)
    {
        const TSharedRef<FJsonObject> Item = MakeShared<FJsonObject>();
        Item->SetStringField(TEXT("id"), Record.Id);
        Item->SetStringField(TEXT("file"), Record.File);
        Item->SetNumberField(TEXT("bytes"), static_cast<double>(Record.Bytes));
        Item->SetStringField(TEXT("sha256"), Record.Sha256);
        Item->SetNumberField(TEXT("tick"), static_cast<double>(Record.Tick));
        Values.Add(MakeShared<FJsonValueObject>(Item));
    }
    Root->SetArrayField(TEXT("captures"), Values);
    SaveJson(FPaths::Combine(ProofRoot, TEXT("capture_receipt.json")), Root);
}

void FSkyguardRecovery03NativeRecovery05Module::WriteRestorationReceipt(
    bool bPassed, const FString& Issue) const
{
    const TSharedRef<FJsonObject> Root = MakeShared<FJsonObject>();
    Root->SetBoolField(TEXT("passed"), bPassed);
    Root->SetStringField(TEXT("issue"), Issue);
    Root->SetStringField(TEXT("original_material_identity"), OriginalMaterialIdentity);
    Root->SetStringField(TEXT("restored_material_identity"), RestoredMaterialIdentity);
    Root->SetBoolField(TEXT("identity_matches"), bRestorationVerified);
    Root->SetBoolField(TEXT("world_saved"), false);
    SaveJson(FPaths::Combine(ProofRoot, TEXT("restoration_receipt.json")), Root);
}

bool FSkyguardRecovery03NativeRecovery05Module::WriteTerminalReceipt(
    bool bPassed, const FString& Issue, int32 ExitCode) const
{
    const TSharedRef<FJsonObject> Root = MakeShared<FJsonObject>();
    Root->SetStringField(TEXT("contract_id"), ContractId);
    Root->SetBoolField(TEXT("passed"), bPassed);
    Root->SetStringField(TEXT("issue"), Issue);
    Root->SetNumberField(TEXT("exit_code"), ExitCode);
    Root->SetNumberField(TEXT("tick_count"), static_cast<double>(TickOrdinal));
    Root->SetNumberField(TEXT("stable_shader_polls"), StableShaderPolls);
    Root->SetNumberField(TEXT("frame_sample_count"), FrameMilliseconds.Num());
    Root->SetNumberField(TEXT("capture_count"), Captures.Num());
    Root->SetBoolField(TEXT("restoration_verified"), bRestorationVerified);
    Root->SetBoolField(TEXT("world_saved"), false);
    Root->SetBoolField(TEXT("asset_imported"), false);
    Root->SetBoolField(TEXT("pcg_generated"), false);
    Root->SetBoolField(TEXT("promotion_performed"), false);
    Root->SetBoolField(TEXT("integration_performed"), false);
    Root->SetBoolField(TEXT("packaging_performed"), false);
    return SaveJson(FPaths::Combine(AttemptRoot, TEXT("terminal_receipt.json")), Root);
}

void FSkyguardRecovery03NativeRecovery05Module::CompleteTerminal(
    bool bPassed, const FString& Issue, int32 ExitCode)
{
    if (bExitRequested)
    {
        return;
    }
    FString RestorationIssue;
    const bool bRestored = RestoreMaterial(RestorationIssue);
    const FString FinalIssue = bRestored
        ? Issue
        : Issue + TEXT("; ") + RestorationIssue;
    const bool bFinalPass = bPassed && bRestored
        && Captures.Num() == RequiredCaptures
        && FrameMilliseconds.Num() >= RequiredFrames;
    WriteFrameSamples();
    WriteCaptureReceipt(bFinalPass, FinalIssue);
    WriteRestorationReceipt(bRestored, RestorationIssue);
    bTerminalReceiptWritten = WriteTerminalReceipt(
        bFinalPass, FinalIssue, bFinalPass ? 0 : ExitCode);
    Phase = EPhase::Terminal;
    bExitRequested = true;
    FPlatformMisc::RequestExitWithStatus(
        false, bTerminalReceiptWritten ? (bFinalPass ? 0 : ExitCode) : 20,
        TEXT("Skyguard Recovery03 Native Recovery01 terminal"));
}

bool FSkyguardRecovery03NativeRecovery05Module::Tick(float DeltaSeconds)
{
    ++TickOrdinal;
    if (FPlatformTime::Seconds() - StartedSeconds > MaximumSeconds)
    {
        CompleteTerminal(false, TEXT("Bounded lifecycle timeout."), 18);
        return false;
    }
    if (Phase == EPhase::Preflight)
    {
        FString Issue;
        if (!VerifyImmutableInputs(Issue) || !VerifyWorldAndAssets(Issue))
        {
            Phase = EPhase::Terminal;
            bExitRequested = true;
            FPlatformMisc::RequestExitWithStatus(
                false, 11,
                TEXT("Skyguard Recovery01 immutable preflight failed before namespace creation"));
            return false;
        }
        if (!CreateFreshOutput(Issue) || !BindTransientMaterial(Issue))
        {
            CompleteTerminal(false, Issue, 12);
            return false;
        }
        AppendHeartbeat(TEXT("preflight_and_binding_complete"));
        StableShaderPolls = 0;
        Phase = EPhase::ShaderWait;
        return true;
    }
    if (Phase == EPhase::ShaderWait)
    {
        FString Issue;
        int32 Finished = 0;
        int32 Valid = 0;
        if (IsShaderReady(Issue, Finished, Valid))
        {
            ++StableShaderPolls;
            AppendHeartbeat(FString::Printf(
                TEXT("shader_ready_%d_finished_%d_valid_%d"),
                StableShaderPolls, Finished, Valid));
        }
        else
        {
            StableShaderPolls = 0;
        }
        if (StableShaderPolls >= RequiredStablePolls)
        {
            Phase = EPhase::Warmup;
            PhaseStartedSeconds = FPlatformTime::Seconds();
        }
        return true;
    }
    if (Phase == EPhase::Warmup)
    {
        FString Issue;
        int32 Finished = 0;
        int32 Valid = 0;
        if (!IsShaderReady(Issue, Finished, Valid))
        {
            StableShaderPolls = 0;
            Phase = EPhase::ShaderWait;
            AppendHeartbeat(TEXT("compilation_resumed_warmup_reset"));
            return true;
        }
        if (FPlatformTime::Seconds() - PhaseStartedSeconds >= WarmupSeconds)
        {
            FrameMilliseconds.Reset();
            GpuMilliseconds.Reset();
            WorkingSetBytes.Reset();
            TextureMemoryBytes.Reset();
            TotalGpuMemoryBytes.Reset();
            AvailableTextureMemoryBytes.Reset();
            PhaseStartedSeconds = FPlatformTime::Seconds();
            Phase = EPhase::Measure;
            AppendHeartbeat(TEXT("measurement_started"));
        }
        return true;
    }
    if (Phase == EPhase::Measure)
    {
        FString Issue;
        int32 Finished = 0;
        int32 Valid = 0;
        if (!IsShaderReady(Issue, Finished, Valid))
        {
            StableShaderPolls = 0;
            FrameMilliseconds.Reset();
            GpuMilliseconds.Reset();
            WorkingSetBytes.Reset();
            TextureMemoryBytes.Reset();
            TotalGpuMemoryBytes.Reset();
            AvailableTextureMemoryBytes.Reset();
            Phase = EPhase::ShaderWait;
            AppendHeartbeat(TEXT("compilation_resumed_measurement_reset"));
            return true;
        }
        FrameMilliseconds.Add(DeltaSeconds * 1000.0);
        GpuMilliseconds.Add(FPlatformTime::ToMilliseconds(RHIGetGPUFrameCycles()));
        const FPlatformMemoryStats Memory = FPlatformMemory::GetStats();
        WorkingSetBytes.Add(Memory.UsedPhysical);
        FTextureMemoryStats TextureStats;
        RHIGetTextureMemoryStats(TextureStats);
        TextureMemoryBytes.Add(TextureStats.StreamingMemorySize + TextureStats.NonStreamingMemorySize);
        TotalGpuMemoryBytes.Add(TextureStats.GetTotalDeviceWorkingMemory());
        AvailableTextureMemoryBytes.Add(TextureStats.ComputeAvailableMemorySize());
        if (FPlatformTime::Seconds() - PhaseStartedSeconds >= MeasureSeconds
            && FrameMilliseconds.Num() >= RequiredFrames)
        {
            Phase = EPhase::Capture;
            CaptureIndex = 0;
            CaptureGapTicks = 0;
            AppendHeartbeat(TEXT("measurement_complete"));
        }
        return true;
    }
    if (Phase == EPhase::Capture)
    {
        if (CaptureGapTicks > 0)
        {
            --CaptureGapTicks;
            return true;
        }
        if (CaptureIndex < RequiredCaptures)
        {
            FString Issue;
            if (!CaptureCurrent(Issue))
            {
                CompleteTerminal(false, Issue, 14);
                return false;
            }
            CaptureGapTicks = CaptureSpecs[CaptureIndex].MinimumGapTicks;
            ++CaptureIndex;
            return true;
        }
        CompleteTerminal(true, FString(), 15);
        return false;
    }
    return Phase != EPhase::Terminal;
}

IMPLEMENT_MODULE(
    FSkyguardRecovery03NativeRecovery05Module,
    SkyguardRecovery03NativeRecovery05)
