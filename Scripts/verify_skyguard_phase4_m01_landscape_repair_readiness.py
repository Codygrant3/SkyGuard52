"""Static, fail-closed readiness verifier for the M01 attempt05 repair.

This verifier never imports Unreal, launches an engine process, authors assets,
or changes the immutable attempt04 evidence. PASS means only that the repair
implementation is statically ready for a C++ recompile in an exclusive lane.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_REPAIR_CONTRACT_ATTEMPT05.json"
)
CAPTURE_SCRIPT = (
    ROOT / "Scripts/capture_skyguard_phase4_m01_landscape_visible_review.py"
)
BUILD_SCRIPT = (
    ROOT
    / "Scripts/build_skyguard_phase4_m01_landscape_material_validation.py"
)
NATIVE_HEADER = (
    ROOT
    / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.h"
)
NATIVE_SOURCE = (
    ROOT
    / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.cpp"
)
PROFILE_HEADER = (
    ROOT / "Source/Skyguard52/SkyguardPhase4LandscapePerformanceCapture.h"
)
PROFILE_SOURCE = (
    ROOT / "Source/Skyguard52/SkyguardPhase4LandscapePerformanceCapture.cpp"
)
COMPILED_MODULE = ROOT / "Binaries/Win64/UnrealEditor-Skyguard52.dll"
COMPILE_LOG_ROOT = ROOT / "Saved/Logs/Phase4Attempt05Compile"
SUPERVISOR = (
    ROOT
    / "Scripts/run_skyguard_phase4_m01_landscape_visible_gpu_gate_attempt05.ps1"
)
ATTEMPT05_CAPTURE = (
    ROOT
    / "Scripts/capture_skyguard_phase4_m01_landscape_visible_review_attempt05.py"
)
ATTEMPT05_GATE = (
    ROOT
    / "Scripts/verify_skyguard_phase4_m01_landscape_visible_gpu_gate_attempt05.py"
)
ATTEMPT05_CONTRACT_LOADER = (
    ROOT / "Scripts/phase4_m01_landscape_repair_contract.py"
)
ENGINE_SCENE_CAPTURE_HEADER = (
    Path(r"D:\UE_5.8")
    / "Engine/Source/Runtime/Engine/Classes/Components/SceneCaptureComponent.h"
)
ENGINE_SHOW_FLAGS_HEADER = (
    Path(r"D:\UE_5.8")
    / "Engine/Source/Runtime/Engine/Public/ShowFlags.h"
)
OUTPUT = (
    ROOT
    / "Saved/Reports"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_REPAIR_READINESS_ATTEMPT05.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    evidence = contract[
        "accepted_attempt04_is_immutable_failed_visual_evidence"
    ]
    map_file = ROOT / evidence["file"]
    material_file = ROOT / evidence["material_file"]
    review_file = ROOT / evidence["human_review_file"]
    capture_source = CAPTURE_SCRIPT.read_text(encoding="utf-8")
    build_source = BUILD_SCRIPT.read_text(encoding="utf-8")
    native_header = NATIVE_HEADER.read_text(encoding="utf-8")
    native_source = NATIVE_SOURCE.read_text(encoding="utf-8")
    profile_header = PROFILE_HEADER.read_text(encoding="utf-8")
    profile_source = PROFILE_SOURCE.read_text(encoding="utf-8")
    supervisor_source = SUPERVISOR.read_text(encoding="utf-8")
    attempt05_capture_source = ATTEMPT05_CAPTURE.read_text(encoding="utf-8")
    attempt05_gate_source = ATTEMPT05_GATE.read_text(encoding="utf-8")
    attempt05_contract_loader_source = ATTEMPT05_CONTRACT_LOADER.read_text(
        encoding="utf-8"
    )
    scene_capture_source = ENGINE_SCENE_CAPTURE_HEADER.read_text(
        encoding="utf-8"
    )
    show_flags_source = ENGINE_SHOW_FLAGS_HEADER.read_text(encoding="utf-8")
    compile_logs = sorted(
        COMPILE_LOG_ROOT.glob("*/build.stdout.log"),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    latest_compile_log = compile_logs[0] if compile_logs else None
    compile_source = (
        latest_compile_log.read_text(encoding="utf-8", errors="replace")
        if latest_compile_log is not None
        else ""
    )
    compile_inputs = (
        NATIVE_HEADER,
        NATIVE_SOURCE,
        PROFILE_HEADER,
        PROFILE_SOURCE,
    )
    module_is_fresh = (
        COMPILED_MODULE.is_file()
        and COMPILED_MODULE.stat().st_mtime_ns
        >= max(path.stat().st_mtime_ns for path in compile_inputs)
    )

    thresholds = contract["capture_revision"][
        "minimum_landscape_pixel_fraction_by_camera"
    ]
    required_audit = contract["authoring_revision"][
        "serialized_and_live_audit"
    ]
    performance = contract["performance_revision"]
    checks = {
        "contract_is_offline_only": (
            contract["execution_authorization"]["unreal_launch_allowed"]
            is False
            and contract["execution_authorization"][
                "candidate_authoring_allowed"
            ]
            is False
            and contract["execution_authorization"]["promotion_allowed"]
            is False
        ),
        "attempt04_map_hash_locked": (
            map_file.is_file()
            and sha256_file(map_file) == evidence["sha256"]
        ),
        "attempt04_material_hash_locked": (
            material_file.is_file()
            and sha256_file(material_file) == evidence["material_sha256"]
        ),
        "attempt04_human_fail_hash_locked": (
            review_file.is_file()
            and sha256_file(review_file)
            == evidence["human_review_sha256"]
        ),
        "attempt05_paths_are_distinct": (
            "attempt05"
            in contract["future_immutable_outputs"]["map"].lower()
            and contract["future_immutable_outputs"]["map"]
            != evidence["map"]
            and contract["future_immutable_outputs"]["material"]
            != evidence["material"]
        ),
        "five_camera_thresholds_declared": (
            set(thresholds)
            == set(contract["capture_revision"]["camera_ids"])
            and all(0.0 < float(value) < 1.0 for value in thresholds.values())
        ),
        "live_component_audit_is_fail_closed": (
            required_audit["landscape_component_count"] == 16
            and required_audit["visible_component_count"] == 16
            and required_audit["registered_component_count"] == 16
            and required_audit[
                "render_state_created_component_count"
            ]
            == 16
            and required_audit[
                "components_with_generated_material_instance"
            ]
            == 16
            and required_audit["hidden_in_game_component_count"] == 0
        ),
        "native_visible_refresh_and_audit_implemented": (
            "PrepareGovernedLandscapeForVisibleValidation" in native_header
            and "AuditLandscapeVisibleReadiness" in native_header
            and "UpdateAllComponentMaterialInstances(true)" in native_source
            and "RecreateRenderState_Concurrent" in native_source
            and "EditorSetLandscapeMaterial" not in native_source
        ),
        "authoring_calls_native_visible_refresh": (
            "prepare_governed_landscape_for_visible_validation"
            in build_source.lower()
            and "build_unlit_diagnostic_material" in build_source
            and "Landscape did not reach live render readiness"
            in build_source
        ),
        "scene_capture_diagnostics_are_native_and_show_only": (
            "ConfigureLandscapeSceneCaptureDiagnostic" in native_header
            and "PRM_UseShowOnlyList" in native_source
            and "ShowOnlyActorComponents" in native_source
            and "configure_landscape_scene_capture_diagnostic"
            in capture_source.lower()
            and "set_transient_landscape_diagnostic_material"
            in capture_source.lower()
        ),
        "same_process_profile_controller_implemented": (
            "UTickableWorldSubsystem" in profile_header
            and "P4_PROFILE_WARMUP_COMPLETE" in profile_source
            and "P4_PROFILE_MEASURED_START" in profile_source
            and "P4_PROFILE_MEASURED_STOP" in profile_source
            and "csvprofile start" in profile_source
            and "csvprofile stop" in profile_source
        ),
        "cpp_compile_and_link_evidence_passes": (
            latest_compile_log is not None
            and module_is_fresh
            and "[1/5] Compile [x64] SkyguardPhase4LandscapePerformanceCapture.cpp"
            in compile_source
            and "[2/5] Compile [x64] SkyguardMission01EnvironmentAuthoringLibrary.cpp"
            in compile_source
            and "[4/5] Link [x64] UnrealEditor-Skyguard52.dll"
            in compile_source
            and "Result: Succeeded" in compile_source
        ),
        "attempt05_wrappers_are_bound_to_attempt05": (
            "load_attempt05_contract" in attempt05_capture_source
            and "load_attempt05_contract" in attempt05_gate_source
            and "PHASE4_M01_LANDSCAPE_VISIBLE_REPAIR_CONTRACT_ATTEMPT05.json"
            in attempt05_contract_loader_source
            and contract["contract_id"]
            == "P4.5-M01-LANDSCAPE-VISIBLE-005"
        ),
        "sequential_supervisor_is_fail_closed": (
            "Start-Job" not in supervisor_source
            and "ForEach-Object -Parallel" not in supervisor_source
            and "-csvCaptureFrames" not in supervisor_source
            and "-AcceptedExitCodes @(0, 2)" in supervisor_source
            and "TECHNICAL_GATE_PASS_PENDING_HUMAN_REVIEW"
            in supervisor_source
            and "Wait-ForZeroHeavyProcesses" in supervisor_source
        ),
        "engine_scene_capture_has_independent_show_flags": (
            "FEngineShowFlags ShowFlags;" in scene_capture_source
            and "SetShowFlagSettings" in scene_capture_source
            and "PRM_UseShowOnlyList" in scene_capture_source
            and "ShowOnlyActorComponents" in scene_capture_source
        ),
        "engine_supports_direct_view_mode_application": (
            "ApplyViewMode(" in show_flags_source
        ),
        "warmup_boundary_is_not_posthoc_filtering": (
            performance["same_process_warmup_and_measurement"] is True
            and performance["boot_capture_forbidden"] is True
            and performance["csvCaptureFrames_switch_forbidden"] is True
            and performance[
                "warmup_seconds_after_world_begin_play_and_camera_ready"
            ]
            == 30
            and performance["measured_seconds"] == 60
        ),
    }
    gate = (
        "PASS_IMPLEMENTATION_COMPILED_READY_PENDING_UNREAL_EXECUTION"
        if all(checks.values())
        else "FAIL_IMPLEMENTATION_STATIC_NOT_READY"
    )
    report = {
        "schema": "skyguard.phase4.m01-landscape-repair-readiness.v1",
        "contract_id": contract["contract_id"],
        "gate": gate,
        "scope": "static implementation and evidence integrity only",
        "unreal_launched": False,
        "candidate_mutated": False,
        "promotion_allowed": False,
        "compile_evidence": {
            "latest_build_stdout": (
                str(latest_compile_log) if latest_compile_log else None
            ),
            "latest_build_stdout_sha256": (
                sha256_file(latest_compile_log)
                if latest_compile_log is not None
                else None
            ),
            "compiled_module": str(COMPILED_MODULE),
            "compiled_module_sha256": (
                sha256_file(COMPILED_MODULE)
                if COMPILED_MODULE.is_file()
                else None
            ),
            "compiled_module_is_fresh_for_attempt05_sources": module_is_fresh,
            "result_succeeded_signature": "Result: Succeeded"
            in compile_source,
        },
        "checks": checks,
        "remaining_before_unreal_execution": [
            "obtain explicit root authorization for one sequential attempt05 run"
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if gate.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
