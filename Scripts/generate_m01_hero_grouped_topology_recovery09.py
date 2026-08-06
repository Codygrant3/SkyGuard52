"""Generate Recovery09 from immutable Recovery07 with exact guarded edits."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE07 = ROOT / (
    "Source/Skyguard52/SkyguardM01GroupedTopologyRecovery07Capture.cpp"
)
HEADER07 = ROOT / (
    "Source/Skyguard52/SkyguardM01GroupedTopologyRecovery07Capture.h"
)
WRAPPER07 = ROOT / (
    "Scripts/"
    "run_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery07.ps1"
)
SOURCE09 = ROOT / (
    "Source/Skyguard52/SkyguardM01GroupedTopologyRecovery09Capture.cpp"
)
HEADER09 = ROOT / (
    "Source/Skyguard52/SkyguardM01GroupedTopologyRecovery09Capture.h"
)
WRAPPER09 = ROOT / (
    "Scripts/"
    "run_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery09.ps1"
)

EXPECTED_INPUTS = {
    SOURCE07: "d8864cc19dc2d99e9d6eb37ddfe9dc48e6285860558b6da74c8edb1b45f221a9",
    HEADER07: "f23d3492e2f7a9a20947a58b5ec51580307a82c2bcd344fcf2b508a171c596e5",
    WRAPPER07: "993500b976d552056cc02f8a8238a17a1ac15755fac5b66db8305d9c78d32aa7",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_exact(text: str, old: str, new: str, count: int = 1) -> str:
    actual = text.count(old)
    if actual != count:
        raise RuntimeError(
            f"Expected {count} exact replacement sites, found {actual}: {old[:80]}"
        )
    return text.replace(old, new)


def rename_recovery(text: str) -> str:
    return (
        text.replace("RECOVERY07", "RECOVERY09")
        .replace("Recovery07", "Recovery09")
        .replace("recovery07", "recovery09")
    )


def generate_header() -> str:
    text = rename_recovery(HEADER07.read_text(encoding="utf-8-sig"))
    text = replace_exact(
        text,
        "\t\tFString Path;\n",
        "\t\tFString Path;\n\t\tFString CompletionMethod;\n",
    )
    text = replace_exact(
        text,
        (
            "\tvoid HandleScreenshotCaptured(\n"
            "\t\tint32 Width,\n"
            "\t\tint32 Height,\n"
            "\t\tconst TArray<FColor>& Colors);\n"
            "\tFCaptureRecord BuildRecord(\n"
            "\t\tint32 Width,\n"
            "\t\tint32 Height,\n"
            "\t\tconst TArray<FColor>& Colors) const;\n"
            "\tbool WritePng(\n"
            "\t\tconst FString& Path,\n"
            "\t\tint32 Width,\n"
            "\t\tint32 Height,\n"
            "\t\tconst TArray<FColor>& Colors) const;\n"
        ),
        (
            "\tvoid HandleScreenshotCaptured(\n"
            "\t\tint32 Width,\n"
            "\t\tint32 Height,\n"
            "\t\tconst TArray<FColor>& Colors);\n"
            "\tbool TryCompleteCurrentCaptureFromFilesystem();\n"
            "\tvoid CompleteCurrentCapture(\n"
            "\t\tint32 Width,\n"
            "\t\tint32 Height,\n"
            "\t\tTArrayView64<const FColor> Colors,\n"
            "\t\tconst FString& CompletionMethod,\n"
            "\t\tbool bPersistPng);\n"
            "\tFCaptureRecord BuildRecord(\n"
            "\t\tint32 Width,\n"
            "\t\tint32 Height,\n"
            "\t\tTArrayView64<const FColor> Colors) const;\n"
            "\tbool WritePng(\n"
            "\t\tconst FString& Path,\n"
            "\t\tint32 Width,\n"
            "\t\tint32 Height,\n"
            "\t\tTArrayView64<const FColor> Colors) const;\n"
            "\tvoid RestoreScreenshotDelegateCVar();\n"
        ),
    )
    text = replace_exact(
        text,
        "\tFString LastReadinessIssue;\n",
        (
            "\tFString LastReadinessIssue;\n"
            "\tFString InitializationFailure;\n"
        ),
    )
    text = replace_exact(
        text,
        "\tint32 ViewIndex = 0;\n",
        (
            "\tint32 ViewIndex = 0;\n"
            "\tint32 PendingFileStableFrames = 0;\n"
            "\tint64 PendingObservedFileSize = -1;\n"
            "\tint32 PreviousScreenshotDelegateValue = 1;\n"
            "\tbool bScreenshotDelegateCVarCaptured = false;\n"
        ),
    )
    return text


def generate_source() -> str:
    text = rename_recovery(SOURCE07.read_text(encoding="utf-8-sig"))
    text = replace_exact(
        text,
        '#include "HAL/FileManager.h"\n',
        '#include "HAL/FileManager.h"\n#include "HAL/IConsoleManager.h"\n',
    )
    text = replace_exact(
        text,
        "\tconstexpr double ScreenshotTimeoutSeconds = 30.0;\n",
        (
            "\tconstexpr double ScreenshotTimeoutSeconds = 45.0;\n"
            "\tconstexpr int32 FilesystemStableFramesRequired = 3;\n"
            "\tconstexpr int64 MinimumPngBytes = 25000;\n"
        ),
    )
    text = replace_exact(
        text,
        '\t\tJson->SetStringField(TEXT("path"), Record.Path);\n',
        (
            '\t\tJson->SetStringField(TEXT("path"), Record.Path);\n'
            '\t\tJson->SetStringField(\n'
            '\t\t\tTEXT("completion_method"),\n'
            "\t\t\tRecord.CompletionMethod);\n"
        ),
    )
    text = replace_exact(
        text,
        (
            "\t\tScreenshotDelegateHandle =\n"
            "\t\t\tFScreenshotRequest::OnScreenshotCaptured().AddUObject(\n"
            "\t\t\t\tthis,\n"
            "\t\t\t\t&USkyguardM01GroupedTopologyRecovery09Capture::\n"
            "\t\t\t\t\tHandleScreenshotCaptured);\n"
        ),
        (
            "\t\tIConsoleVariable* ScreenshotDelegateCVar =\n"
            "\t\t\tIConsoleManager::Get().FindConsoleVariable(\n"
            '\t\t\t\tTEXT("r.ScreenshotDelegate"));\n'
            "\t\tif (!ScreenshotDelegateCVar)\n"
            "\t\t{\n"
            "\t\t\tInitializationFailure =\n"
            '\t\t\t\tTEXT("r.ScreenshotDelegate is unavailable.");\n'
            "\t\t}\n"
            "\t\telse\n"
            "\t\t{\n"
            "\t\t\tPreviousScreenshotDelegateValue =\n"
            "\t\t\t\tScreenshotDelegateCVar->GetInt();\n"
            "\t\t\tbScreenshotDelegateCVarCaptured = true;\n"
            "\t\t\tScreenshotDelegateCVar->Set(1, ECVF_SetByCode);\n"
            "\t\t\tScreenshotDelegateHandle =\n"
            "\t\t\t\tUGameViewportClient::OnScreenshotCaptured().AddUObject(\n"
            "\t\t\t\t\tthis,\n"
            "\t\t\t\t\t&USkyguardM01GroupedTopologyRecovery09Capture::\n"
            "\t\t\t\t\t\tHandleScreenshotCaptured);\n"
            "\t\t}\n"
        ),
    )
    text = replace_exact(
        text,
        (
            "\t\tFScreenshotRequest::OnScreenshotCaptured().Remove(\n"
            "\t\t\tScreenshotDelegateHandle);\n"
        ),
        (
            "\t\tUGameViewportClient::OnScreenshotCaptured().Remove(\n"
            "\t\t\tScreenshotDelegateHandle);\n"
        ),
    )
    text = replace_exact(
        text,
        "\tGetHighResScreenshotConfig().SetFilename(FString());\n\tRestoreVisibility();\n",
        (
            "\tGetHighResScreenshotConfig().SetFilename(FString());\n"
            "\tRestoreScreenshotDelegateCVar();\n"
            "\tRestoreVisibility();\n"
        ),
    )
    text = replace_exact(
        text,
        (
            "\tconst double Now = FPlatformTime::Seconds();\n"
            "\tif (Now - SessionStartSeconds > AbsoluteSessionTimeoutSeconds)\n"
        ),
        (
            "\tconst double Now = FPlatformTime::Seconds();\n"
            "\tif (!InitializationFailure.IsEmpty())\n"
            "\t{\n"
            "\t\tFail(InitializationFailure);\n"
            "\t\treturn;\n"
            "\t}\n"
            "\tif (Now - SessionStartSeconds > AbsoluteSessionTimeoutSeconds)\n"
        ),
    )
    text = replace_exact(
        text,
        (
            "\tif (bScreenshotPending)\n"
            "\t{\n"
            "\t\tif (Now - RequestStartSeconds > ScreenshotTimeoutSeconds)\n"
        ),
        (
            "\tif (bScreenshotPending)\n"
            "\t{\n"
            "\t\tif (TryCompleteCurrentCaptureFromFilesystem())\n"
            "\t\t{\n"
            "\t\t\treturn;\n"
            "\t\t}\n"
            "\t\tif (Now - RequestStartSeconds > ScreenshotTimeoutSeconds)\n"
        ),
    )
    text = replace_exact(
        text,
        (
            "\tbScreenshotPending = true;\n"
            "\tRequestStartSeconds = FPlatformTime::Seconds();\n"
        ),
        (
            "\tif (IFileManager::Get().FileExists(*PendingPath))\n"
            "\t{\n"
            "\t\tFail(TEXT(\"Recovery09 output path already exists.\"));\n"
            "\t\treturn;\n"
            "\t}\n"
            "\tPendingObservedFileSize = -1;\n"
            "\tPendingFileStableFrames = 0;\n"
            "\tbScreenshotPending = true;\n"
            "\tRequestStartSeconds = FPlatformTime::Seconds();\n"
        ),
    )

    callback_start = text.index(
        "void USkyguardM01GroupedTopologyRecovery09Capture::\n"
        "\tHandleScreenshotCaptured("
    )
    build_start = text.index(
        "USkyguardM01GroupedTopologyRecovery09Capture::FCaptureRecord\n"
        "USkyguardM01GroupedTopologyRecovery09Capture::BuildRecord(",
        callback_start,
    )
    old_callback = text[callback_start:build_start]
    complete = old_callback.replace(
        (
            "void USkyguardM01GroupedTopologyRecovery09Capture::\n"
            "\tHandleScreenshotCaptured(\n"
            "\t\tconst int32 Width,\n"
            "\t\tconst int32 Height,\n"
            "\t\tconst TArray<FColor>& Colors)\n"
        ),
        (
            "void USkyguardM01GroupedTopologyRecovery09Capture::\n"
            "\tCompleteCurrentCapture(\n"
            "\t\tconst int32 Width,\n"
            "\t\tconst int32 Height,\n"
            "\t\tconst TArrayView64<const FColor> Colors,\n"
            "\t\tconst FString& CompletionMethod,\n"
            "\t\tconst bool bPersistPng)\n"
        ),
        1,
    )
    complete = complete.replace(
        "\tRecord.Path = PendingPath;\n",
        (
            "\tRecord.Path = PendingPath;\n"
            "\tRecord.CompletionMethod = CompletionMethod;\n"
        ),
        1,
    )
    complete = replace_exact(
        complete,
        (
            '\t\t\t"[RECOVERY09][CAPTURE_CALLBACK] family=%s view=%s "\n'
            '\t\t\t"callback=%dx%d live=%s hard_bounds=%s"),\n'
            "\t\t*PendingFamily,\n"
        ),
        (
            '\t\t\t"[RECOVERY09][CAPTURE_COMPLETE] method=%s "\n'
            '\t\t\t"family=%s view=%s pixels=%dx%d live=%s "\n'
            '\t\t\t"hard_bounds=%s"),\n'
            "\t\t*CompletionMethod,\n"
            "\t\t*PendingFamily,\n"
        ),
    )
    complete = complete.replace(
        "\tif (!WritePng(PendingPath, Width, Height, Colors))\n",
        "\tif (bPersistPng && !WritePng(PendingPath, Width, Height, Colors))\n",
        1,
    )
    if complete == old_callback:
        raise RuntimeError("Callback transformation made no changes")

    prefix = (
        "void USkyguardM01GroupedTopologyRecovery09Capture::\n"
        "\tHandleScreenshotCaptured(\n"
        "\t\tconst int32 Width,\n"
        "\t\tconst int32 Height,\n"
        "\t\tconst TArray<FColor>& Colors)\n"
        "{\n"
        "\tCompleteCurrentCapture(\n"
        "\t\tWidth,\n"
        "\t\tHeight,\n"
        "\t\tTArrayView64<const FColor>(Colors.GetData(), Colors.Num()),\n"
        '\t\tTEXT("game_viewport_delegate"),\n'
        "\t\ttrue);\n"
        "}\n\n"
        "bool USkyguardM01GroupedTopologyRecovery09Capture::\n"
        "\tTryCompleteCurrentCaptureFromFilesystem()\n"
        "{\n"
        "\tconst int64 FileSize = IFileManager::Get().FileSize(*PendingPath);\n"
        "\tif (FileSize < MinimumPngBytes)\n"
        "\t{\n"
        "\t\tPendingObservedFileSize = FileSize;\n"
        "\t\tPendingFileStableFrames = 0;\n"
        "\t\treturn false;\n"
        "\t}\n"
        "\tif (FileSize != PendingObservedFileSize)\n"
        "\t{\n"
        "\t\tPendingObservedFileSize = FileSize;\n"
        "\t\tPendingFileStableFrames = 1;\n"
        "\t\treturn false;\n"
        "\t}\n"
        "\t++PendingFileStableFrames;\n"
        "\tif (PendingFileStableFrames < FilesystemStableFramesRequired)\n"
        "\t{\n"
        "\t\treturn false;\n"
        "\t}\n"
        "\tTArray<uint8> PngBytes;\n"
        "\tif (!FFileHelper::LoadFileToArray(PngBytes, *PendingPath)\n"
        "\t\t|| PngBytes.Num() < 24\n"
        "\t\t|| PngBytes[0] != 0x89 || PngBytes[1] != 0x50\n"
        "\t\t|| PngBytes[2] != 0x4e || PngBytes[3] != 0x47\n"
        "\t\t|| PngBytes[12] != 0x49 || PngBytes[13] != 0x48\n"
        "\t\t|| PngBytes[14] != 0x44 || PngBytes[15] != 0x52)\n"
        "\t{\n"
        '\t\tFail(TEXT("Stable screenshot file is not a valid PNG IHDR."));\n'
        "\t\treturn true;\n"
        "\t}\n"
        "\tconst int32 PngWidth =\n"
        "\t\t(static_cast<int32>(PngBytes[16]) << 24)\n"
        "\t\t| (static_cast<int32>(PngBytes[17]) << 16)\n"
        "\t\t| (static_cast<int32>(PngBytes[18]) << 8)\n"
        "\t\t| static_cast<int32>(PngBytes[19]);\n"
        "\tconst int32 PngHeight =\n"
        "\t\t(static_cast<int32>(PngBytes[20]) << 24)\n"
        "\t\t| (static_cast<int32>(PngBytes[21]) << 16)\n"
        "\t\t| (static_cast<int32>(PngBytes[22]) << 8)\n"
        "\t\t| static_cast<int32>(PngBytes[23]);\n"
        "\tFSceneViewport* SceneViewport =\n"
        "\t\tGEngine && GEngine->GameViewport\n"
        "\t\t\t? GEngine->GameViewport->GetGameViewport()\n"
        "\t\t\t: nullptr;\n"
        "\tTArray<FColor> Colors;\n"
        "\tif (!SceneViewport || !SceneViewport->ReadPixels(Colors))\n"
        "\t{\n"
        '\t\tFail(TEXT("Stable PNG fallback live readback failed."));\n'
        "\t\treturn true;\n"
        "\t}\n"
        "\tconst FIntPoint LiveSize = SceneViewport->GetSizeXY();\n"
        "\tif (PngWidth != RequiredWidth || PngHeight != RequiredHeight\n"
        "\t\t|| LiveSize.X != PngWidth || LiveSize.Y != PngHeight\n"
        "\t\t|| Colors.Num() != PngWidth * PngHeight)\n"
        "\t{\n"
        '\t\tFail(TEXT("Stable PNG and live readback dimensions differ."));\n'
        "\t\treturn true;\n"
        "\t}\n"
        "\tCompleteCurrentCapture(\n"
        "\t\tPngWidth,\n"
        "\t\tPngHeight,\n"
        "\t\tTArrayView64<const FColor>(Colors.GetData(), Colors.Num()),\n"
        '\t\tTEXT("stable_filesystem_png_plus_live_readback"),\n'
        "\t\tfalse);\n"
        "\treturn true;\n"
        "}\n\n"
    )
    text = text[:callback_start] + prefix + complete + text[build_start:]
    text = text.replace(
        "\t\tconst TArray<FColor>& Colors) const\n",
        "\t\tconst TArrayView64<const FColor> Colors) const\n",
        2,
    )
    text = replace_exact(
        text,
        (
            "\tFImageUtils::PNGCompressImageArray(\n"
            "\t\tWidth,\n"
            "\t\tHeight,\n"
            "\t\tTArrayView64<const FColor>(Colors.GetData(), Colors.Num()),\n"
            "\t\tCompressed);\n"
        ),
        (
            "\tFImageUtils::PNGCompressImageArray(\n"
            "\t\tWidth,\n"
            "\t\tHeight,\n"
            "\t\tColors,\n"
            "\t\tCompressed);\n"
        ),
    )
    text = replace_exact(
        text,
        (
            '\t\tTEXT("capture_resolution_path"),\n'
            "\t\tTEXT(\n"
            '\t\t\t"FHighResScreenshotConfig::SetResolution+"\n'
            '\t\t\t"FViewport::TakeHighResScreenShot"));\n'
        ),
        (
            '\t\tTEXT("capture_resolution_path"),\n'
            "\t\tTEXT(\n"
            '\t\t\t"FHighResScreenshotConfig::SetResolution+"\n'
            '\t\t\t"FViewport::TakeHighResScreenShot+"\n'
            '\t\t\t"UGameViewportClient::OnScreenshotCaptured"));\n'
            "\tReceipt->SetStringField(\n"
            '\t\tTEXT("completion_fallback"),\n'
            '\t\tTEXT("stable_filesystem_png_plus_live_readback"));\n'
        ),
    )
    restore_marker = (
        "void USkyguardM01GroupedTopologyRecovery09Capture::RestoreVisibility()\n"
    )
    restore_method = (
        "void USkyguardM01GroupedTopologyRecovery09Capture::\n"
        "\tRestoreScreenshotDelegateCVar()\n"
        "{\n"
        "\tif (!bScreenshotDelegateCVarCaptured)\n"
        "\t{\n"
        "\t\treturn;\n"
        "\t}\n"
        "\tif (IConsoleVariable* ScreenshotDelegateCVar =\n"
        "\t\tIConsoleManager::Get().FindConsoleVariable(\n"
        '\t\t\tTEXT("r.ScreenshotDelegate")))\n'
        "\t{\n"
        "\t\tScreenshotDelegateCVar->Set(\n"
        "\t\t\tPreviousScreenshotDelegateValue,\n"
        "\t\t\tECVF_SetByCode);\n"
        "\t}\n"
        "\tbScreenshotDelegateCVarCaptured = false;\n"
        "}\n\n"
    )
    text = replace_exact(
        text,
        restore_marker,
        restore_method + restore_marker,
    )
    return text


def generate_wrapper() -> str:
    text = rename_recovery(WRAPPER07.read_text(encoding="utf-8-sig"))
    text = replace_exact(
        text,
        '$combined -notmatch "\\[RECOVERY09\\]\\[CAPTURE_CALLBACK\\]"',
        '$combined -notmatch "\\[RECOVERY09\\]\\[CAPTURE_COMPLETE\\]"',
    )
    return text


def main() -> None:
    for path, expected in EXPECTED_INPUTS.items():
        if sha256(path) != expected:
            raise RuntimeError(f"Immutable input hash mismatch: {path}")
    outputs = {
        HEADER09: generate_header(),
        SOURCE09: generate_source(),
        WRAPPER09: generate_wrapper(),
    }
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"{path} {path.stat().st_size} {sha256(path)}")


if __name__ == "__main__":
    main()
