"""Offline Recovery09 design audit; never builds or launches Unreal/Blender."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY09_DESIGN_CONTRACT.json"
)
OUTPUT_PATH = ROOT / (
    "Saved/Reports/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY09_DESIGN_READINESS.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def exact(record: dict) -> bool:
    path = resolve(record["path"])
    return (
        path.is_file()
        and path.stat().st_size == record["bytes"]
        and sha256_file(path) == record["sha256"]
    )


def add(checks: list[dict], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def png_ihdr(path: Path) -> tuple[str, str, int, int]:
    data = path.read_bytes()[:24]
    return (
        data[:8].hex(),
        data[12:16].decode("ascii", errors="replace"),
        int.from_bytes(data[16:20], "big"),
        int.from_bytes(data[20:24], "big"),
    )


def audit(write_report: bool = True) -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    checks: list[dict] = []

    failure = contract["recovery07_terminal_failure"]
    failure_records = (
        failure["supervisor_receipt"],
        failure["capture_receipt"],
        failure["written_pilot_png"],
        failure["unreal_engine_log"],
        failure["unreal_stdout"],
    )
    add(
        checks,
        "recovery07_terminal_evidence_hash_bound",
        all(exact(record) for record in failure_records)
        and failure["immutable"]
        and failure["retry_in_same_namespace_forbidden"],
        "terminal receipts, logs, and written PNG remain exact and immutable",
    )
    supervisor = json.loads(
        resolve(failure["supervisor_receipt"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    capture = json.loads(
        resolve(failure["capture_receipt"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    add(
        checks,
        "recovery07_gates_and_counts_are_terminal_fail",
        supervisor["gate"] == failure["supervisor_receipt"]["gate"]
        and capture["gate"] == failure["capture_receipt"]["gate"]
        and capture["issue"] == failure["capture_receipt"]["issue"]
        and capture["pilot_capture_count"] == 0
        and capture["full_view_capture_count"] == 0,
        "supervisor and capture receipts fail closed with zero accepted captures",
    )
    png = failure["written_pilot_png"]
    signature, chunk, width, height = png_ihdr(resolve(png["path"]))
    add(
        checks,
        "written_png_is_exact_2048_ihdr",
        signature == png["png_signature_hex"]
        and chunk == "IHDR"
        and width == png["ihdr_width"] == 2048
        and height == png["ihdr_height"] == 2048,
        f"PNG signature={signature}, IHDR={width}x{height}",
    )
    engine_log = resolve(failure["unreal_engine_log"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "runtime_sequence_proves_disk_write_without_callback",
        "[RECOVERY07][CAPTURE_REQUEST]" in engine_log
        and 'Tracing Screenshot "Pilot_00" taken with size: 2048 x 2048'
        in engine_log
        and "High resolution screenshot saved as" in engine_log
        and "[RECOVERY07][CAPTURE_CALLBACK]" not in engine_log
        and "[RECOVERY07][FAIL]" in engine_log,
        "request, exact capture, disk save, missing callback, bounded fail",
    )

    ue = contract["ue58_root_cause_evidence"]
    add(
        checks,
        "installed_ue58_evidence_hash_bound",
        exact(ue["game_viewport_client_source"])
        and exact(ue["game_viewport_client_header"]),
        "installed GameViewportClient source and header remain exact",
    )
    ue_source = resolve(ue["game_viewport_client_source"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    ue_header = resolve(ue["game_viewport_client_header"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "ue58_delegate_branch_confirms_root_cause",
        'TEXT("r.ScreenshotDelegate")' in ue_source
        and "ScreenshotCapturedDelegate.IsBound()" in ue_source
        and "ScreenshotCapturedDelegate.Broadcast(Size.X, Size.Y, Bitmap);"
        in ue_source
        and "ProcessScreenshotData(Bitmap" in ue_source
        and "static FOnScreenshotCaptured& OnScreenshotCaptured()" in ue_header,
        "UGameViewportClient broadcasts its own delegate or writes to disk",
    )

    preserved = contract["preserved_recovery07_08"]
    preserved_records = tuple(
        record
        for key, record in preserved.items()
        if isinstance(record, dict) and "path" in record
    )
    add(
        checks,
        "recovery07_08_remain_byte_identical",
        all(exact(record) for record in preserved_records)
        and preserved["must_remain_byte_identical"],
        f"{len(preserved_records)} preserved Recovery07/08 inputs exact",
    )

    implementation = contract["recovery09_implementation"]
    implementation_records = (
        implementation["generator"],
        implementation["header"],
        implementation["source"],
        implementation["future_wrapper"],
    )
    add(
        checks,
        "recovery09_artifacts_hash_bound",
        all(exact(record) for record in implementation_records),
        "generator, source, header, and wrapper are exact",
    )
    source = resolve(implementation["source"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    header = resolve(implementation["header"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    add(
        checks,
        "correct_game_viewport_delegate_is_used",
        source.count(
            "UGameViewportClient::OnScreenshotCaptured().AddUObject("
        )
        == 1
        and source.count(
            "UGameViewportClient::OnScreenshotCaptured().Remove("
        )
        == 1
        and "FScreenshotRequest::OnScreenshotCaptured" not in source
        and "game_viewport_delegate" in source,
        "Recovery09 binds and removes the UE 5.8 broadcast delegate",
    )
    add(
        checks,
        "screenshot_delegate_cvar_is_forced_and_restored",
        source.count('TEXT("r.ScreenshotDelegate")') == 2
        and "PreviousScreenshotDelegateValue" in source
        and "ScreenshotDelegateCVar->Set(1, ECVF_SetByCode);" in source
        and "RestoreScreenshotDelegateCVar();" in source
        and "bScreenshotDelegateCVarCaptured = false;" in source,
        "delegate cvar is deterministic and previous value is restored",
    )
    add(
        checks,
        "filesystem_fallback_matches_observed_behavior",
        "FilesystemStableFramesRequired = 3" in source
        and "MinimumPngBytes = 25000" in source
        and "FFileHelper::LoadFileToArray(PngBytes, *PendingPath)" in source
        and "PngBytes[12] != 0x49" in source
        and "SceneViewport->ReadPixels(Colors)" in source
        and "stable_filesystem_png_plus_live_readback" in source,
        "stable PNG IHDR plus exact live viewport readback is the fallback",
    )
    add(
        checks,
        "completion_is_recorded_and_dimension_gated",
        "FString CompletionMethod;" in header
        and 'TEXT("completion_method")' in source
        and "[RECOVERY09][CAPTURE_COMPLETE]" in source
        and "Width != RequiredWidth || Height != RequiredHeight" in source
        and "Colors.Num() != PngWidth * PngHeight" in source,
        "each accepted capture records method and exact dimensions",
    )
    add(
        checks,
        "timeouts_and_failure_paths_are_bounded",
        "ScreenshotTimeoutSeconds = 45.0" in source
        and "AbsoluteSessionTimeoutSeconds = 300.0" in source
        and "TryCompleteCurrentCaptureFromFilesystem()" in source
        and "FAIL_CLOSED_RECOVERY09_HIGHRES_CAPTURE" in source
        and "RequestExitWithStatus" in source,
        "45-second per-capture and 300-second session bounds fail closed",
    )
    add(
        checks,
        "no_new_module_dependency_or_rules_change",
        implementation["no_new_module_dependency"]
        and implementation["module_rules_unchanged"]
        and exact(preserved["module_rules"])
        and '#include "ImageCore.h"' not in source
        and "IImageWrapper" not in source,
        "fallback uses existing Engine/Core APIs; Build.cs remains frozen",
    )

    wrapper = resolve(implementation["future_wrapper"]["path"]).read_text(
        encoding="utf-8-sig"
    )
    future = contract["future_build"]
    add(
        checks,
        "future_wrapper_is_hash_gated_and_execution_contract_absent",
        "AuthorizeSingleRecovery09Run" in wrapper
        and "ExpectedExecutionContractSha256" in wrapper
        and "RECOVERY09_EXECUTION_CONTRACT.json" in wrapper
        and "[RECOVERY09\\]\\[CAPTURE_COMPLETE\\]" in wrapper
        and not resolve(future["post_build_execution_contract_path"]).exists()
        and future["post_build_execution_contract_currently_absent"],
        "future run requires explicit switch and post-build contract hash",
    )

    output = contract["future_output"]
    add(
        checks,
        "recovery09_namespace_is_distinct_and_absent",
        output["distinct_from_recovery07"]
        and output["attempt_root"] != failure["output_root"]
        and not resolve(output["attempt_root"]).exists()
        and not resolve(output["capture_root"]).exists()
        and output["overwrite_or_retry_in_same_namespace"] is False,
        f"new absent namespace: {output['attempt_root']}",
    )
    add(
        checks,
        "build_and_launch_remain_unauthorized",
        future["requires_separate_authorization"]
        and future["unreal_launch_allowed_during_build"] is False
        and contract["native_build_authorized"] is False
        and contract["native_build_executed"] is False
        and contract["unreal_launch_authorized"] is False
        and contract["unreal_launched"] is False
        and contract["blender_launched"] is False,
        "offline design only; build and execution require later handoffs",
    )
    add(
        checks,
        "never_promotes_or_closes",
        contract["content_packages_created_or_modified"] == 0
        and contract["promotion_allowed"] is False
        and contract["p3_4_closed"] is False,
        "Recovery09 design cannot promote evidence or close P3.4",
    )

    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": (
            "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03."
            "recovery09-design-readiness.v1"
        ),
        "gate": (
            "PASS_OFFLINE_RECOVERY09_DESIGN_READY_"
            "AWAITING_SEPARATE_FULL_MODULE_BUILD_AUTHORIZATION"
            if not failures
            else "FAIL_OFFLINE_RECOVERY09_DESIGN_NOT_READY"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "contract": CONTRACT_PATH.relative_to(ROOT).as_posix(),
        "checks": checks,
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "failure_count": len(failures),
        "failures": failures,
        "native_build_executed": False,
        "unreal_launched": False,
        "blender_launched": False,
    }
    if write_report:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
    return report


if __name__ == "__main__":
    result = audit(write_report=True)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["failure_count"] == 0 else 1)
