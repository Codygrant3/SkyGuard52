"""Single-run fail-closed supervisor for immutable Phase 4 Attempt06.

This file defines the authorized future execution. Importing it is inert.
Execution requires --authorize-single-run, an empty heavy lane, absent
Attempt06 outputs, and exact immutable predecessor hashes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_ROOT = Path(r"D:\Skyguard52")
DEFAULT_UNREAL_ROOT = Path(r"D:\UE_5.8")
HEAVY_NAMES = {
    "unrealeditor.exe",
    "unrealeditor-cmd.exe",
    "unrealbuildtool.exe",
    "automationtool.exe",
    "shadercompileworker.exe",
    "ubaagent.exe",
    "ubaserver.exe",
    "crashreportclient.exe",
    "skyguard52.exe",
    "blender.exe",
}
CRITICAL_SIGNATURES = (
    "Fatal error",
    "Assertion failed",
    "GPU Crash",
    "DXGI_ERROR_DEVICE_",
    "Out of video memory",
    "LogPython: Error",
    "Traceback (most recent call last)",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def read_contract(root: Path) -> dict:
    path = (
        root
        / "Docs/AAA_Review/"
        "PHASE4_M01_LANDSCAPE_VISIBLE_REPAIR_CONTRACT_ATTEMPT06.json"
    )
    return json.loads(path.read_text(encoding="utf-8-sig"))


def active_heavy_processes() -> list[dict]:
    completed = subprocess.run(
        ["tasklist", "/fo", "csv", "/nh"],
        capture_output=True,
        text=True,
        check=True,
    )
    processes = []
    for row in csv.reader(completed.stdout.splitlines()):
        if len(row) < 2 or row[0].lower() not in HEAVY_NAMES:
            continue
        processes.append({"name": row[0], "pid": int(row[1])})
    return processes


def wait_for_zero_heavy_processes(timeout_seconds: int = 30) -> list[dict]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        active = active_heavy_processes()
        if not active:
            return []
        time.sleep(1)
    return active_heavy_processes()


def terminate_owned_tree(process: subprocess.Popen) -> None:
    subprocess.run(
        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
        capture_output=True,
        text=True,
        check=False,
    )


def run_stage(
    name: str,
    executable: Path | str,
    arguments: list[str],
    logs_root: Path,
    project_root: Path,
    timeout_seconds: int,
    accepted_exit_codes: tuple[int, ...] = (0,),
) -> dict:
    stdout_path = logs_root / f"{name}.stdout.log"
    stderr_path = logs_root / f"{name}.stderr.log"
    engine_log = logs_root / f"{name}.engine.log"
    final_arguments = list(arguments)
    executable_path = str(executable)
    if Path(executable_path).name.lower() in {
        "unrealeditor.exe",
        "unrealeditor-cmd.exe",
    }:
        final_arguments.append(f"-abslog={engine_log}")
    started = utc_now()
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr:
        process = subprocess.Popen(
            [executable_path, *final_arguments],
            cwd=project_root,
            stdout=stdout,
            stderr=stderr,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        timed_out = False
        try:
            exit_code = process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            timed_out = True
            terminate_owned_tree(process)
            exit_code = process.wait(timeout=30)
    combined = ""
    for path in (stdout_path, stderr_path, engine_log):
        if path.is_file():
            combined += path.read_text(
                encoding="utf-8", errors="replace"
            )
    critical = [
        signature for signature in CRITICAL_SIGNATURES
        if signature.lower() in combined.lower()
    ]
    stage = {
        "name": name,
        "command": [executable_path, *final_arguments],
        "started_at_utc": started,
        "finished_at_utc": utc_now(),
        "timeout_seconds": timeout_seconds,
        "timed_out": timed_out,
        "process_exit_observed": process.poll() is not None,
        "exit_code": exit_code,
        "stdout": str(stdout_path),
        "stderr": str(stderr_path),
        "engine_log": str(engine_log),
        "critical_log_signatures": critical,
    }
    if timed_out or exit_code not in accepted_exit_codes or critical:
        raise RuntimeError(
            f"stage failed: {name}; timed_out={timed_out}; "
            f"exit={exit_code}; critical={critical}"
        )
    return stage


def csv_roots(root: Path) -> tuple[Path, ...]:
    local_app_data = Path(os.environ.get("LOCALAPPDATA", r"C:\Users\Default"))
    return (
        root / "Saved/Profiling/CSV",
        local_app_data / "UnrealEngine/5.8/Saved/Profiling/CSV",
    )


def csv_files(root: Path) -> set[Path]:
    return {
        path.resolve()
        for csv_root in csv_roots(root)
        if csv_root.is_dir()
        for path in csv_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".csv", ".gz"}
    }


def newest_new_csv(
    root: Path, before: set[Path], started_epoch: float
) -> Path:
    candidates = [
        path
        for path in csv_files(root) - before
        if path.stat().st_size > 0
        and path.stat().st_mtime >= started_epoch - 2.0
    ]
    if not candidates:
        raise RuntimeError("profile produced no new nonempty CSV")
    return max(candidates, key=lambda path: path.stat().st_mtime_ns)


def assert_locked_items(root: Path, items: dict) -> dict[str, str]:
    snapshot = {}
    for name, item in items.items():
        if not isinstance(item, dict) or "file" not in item:
            continue
        path = root / item["file"]
        if not path.is_file():
            raise RuntimeError(f"missing immutable file: {path}")
        actual = sha256_file(path)
        if actual != item["sha256"]:
            raise RuntimeError(f"immutable hash failed: {path}")
        snapshot[name] = actual
    return snapshot


def capture_manifest_pass(path: Path, expected_files: int) -> bool:
    if not path.is_file():
        return False
    manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    return bool(
        manifest.get("contract_id")
        == "P4.5-M01-LANDSCAPE-VISIBLE-006"
        and manifest.get("rhi_validation") == "D3D12|SM6"
        and manifest.get("files_complete_at_script_exit") is True
        and len(manifest.get("files", [])) == expected_files
        and manifest.get("world_saved") is False
        and manifest.get("pcg_generation_invoked") is False
        and manifest.get("camera_transform_authority") == "contract_only"
        and manifest.get("serialized_camera_actor_fallback_used") is False
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--unreal-root", type=Path, default=DEFAULT_UNREAL_ROOT)
    parser.add_argument("--authorize-single-run", action="store_true")
    parser.add_argument("--build-timeout", type=int, default=900)
    parser.add_argument("--editor-timeout", type=int, default=300)
    parser.add_argument("--profile-timeout", type=int, default=150)
    args = parser.parse_args()
    if not args.authorize_single_run:
        raise RuntimeError(
            "Attempt06 execution requires explicit --authorize-single-run"
        )
    root = args.project_root.resolve()
    unreal_root = args.unreal_root.resolve()
    contract = read_contract(root)
    if contract["contract_id"] != "P4.5-M01-LANDSCAPE-VISIBLE-006":
        raise RuntimeError("Attempt06 contract ID mismatch")
    if active_heavy_processes():
        raise RuntimeError("exclusive heavy lane is not free")
    predecessor = contract["immutable_predecessor"]
    predecessor_evidence = assert_locked_items(
        root,
        {
            "recovery_manifest": predecessor["recovery_manifest"],
            "gate_report": predecessor["gate_report"],
        },
    )
    predecessor_packages = assert_locked_items(
        root, predecessor["package_hashes"]
    )
    outputs = contract["future_immutable_outputs"]
    output_paths = {
        key: root / outputs[key]
        for key in (
            "map_file",
            "material_file",
            "coverage_material_file",
            "component_id_material_file",
        )
    }
    attempt_root_parent = root / outputs["attempt_root"]
    if attempt_root_parent.exists() or any(
        path.exists() for path in output_paths.values()
    ):
        raise RuntimeError(
            "Attempt06 output/root already exists; refusing duplicate or overwrite"
        )
    project = root / "Skyguard52.uproject"
    build_tool = unreal_root / "Engine/Build/BatchFiles/Build.bat"
    editor_cmd = (
        unreal_root / "Engine/Binaries/Win64/UnrealEditor-Cmd.exe"
    )
    editor = unreal_root / "Engine/Binaries/Win64/UnrealEditor.exe"
    scripts = {
        "author": root
        / "Scripts/build_skyguard_phase4_m01_landscape_material_validation_attempt06.py",
        "editor_verify": root
        / "Scripts/verify_skyguard_phase4_m01_landscape_material_assets_attempt06.py",
        "capture": root
        / "Scripts/capture_skyguard_phase4_m01_landscape_visible_review_attempt06.py",
        "gate": root
        / "Scripts/verify_skyguard_phase4_m01_landscape_visible_gpu_gate_attempt06.py",
    }
    for required in (
        project,
        build_tool,
        editor_cmd,
        editor,
        *scripts.values(),
    ):
        if not required.is_file():
            raise RuntimeError(f"required file missing: {required}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    attempt_id = "attempt_" + stamp[:-3] + "Z"
    attempt_root = attempt_root_parent / attempt_id
    logs_root = attempt_root / "logs"
    artifacts_root = attempt_root / "artifacts"
    captures_root = artifacts_root / "captures"
    logs_root.mkdir(parents=True, exist_ok=False)
    captures_root.mkdir(parents=True, exist_ok=False)
    manifest_path = attempt_root / "run_manifest.json"
    gate_path = attempt_root / "gate_report.json"
    latest_gate = (
        root
        / "Saved/Reports/"
        "PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_ATTEMPT06_LATEST.json"
    )
    baseline_map = (
        "/Game/Skyguard/Maps/"
        "Lvl_M01_CoastalIntercept_ProductionEnvironment_v5_attempt03"
    )
    candidate_map = outputs["map"]
    manifest = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-attempt06-supervisor.v1"
        ),
        "contract_id": contract["contract_id"],
        "attempt_id": attempt_id,
        "created_at_utc": utc_now(),
        "controls": {
            "single_authorized_run": True,
            "sequential_processes_only": True,
            "active_rhi_required": "D3D12|SM6",
            "pcg_generation_allowed": False,
            "world_or_package_save_during_capture_allowed": False,
            "network_download_allowed": False,
            "automatic_retry_allowed": False,
            "promotion_allowed": False,
            "boot_csv_capture_forbidden": True,
            "warmup_seconds": 30,
            "measured_seconds": 60,
        },
        "predecessor_evidence_before": predecessor_evidence,
        "predecessor_packages_before": predecessor_packages,
        "stages": [],
        "artifacts": {
            "baseline_capture_root": str(captures_root / "baseline"),
            "candidate_capture_root": str(captures_root / "candidate"),
            "baseline_profile_receipt": str(
                artifacts_root / "baseline_profile_receipt.json"
            ),
            "candidate_profile_receipt": str(
                artifacts_root / "candidate_profile_receipt.json"
            ),
            "baseline_csv": None,
            "candidate_csv": None,
            "editor_acceptance": str(
                root
                / "Saved/Reports/"
                "PHASE4_M01_LANDSCAPE_MATERIAL_EDITOR_ACCEPTANCE_ATTEMPT06.json"
            ),
        },
        "candidate_hashes_before_evidence": {},
        "candidate_hashes_after_evidence": {},
        "terminal_state": "RUNNING",
        "errors": [],
    }
    save_json(manifest_path, manifest)
    try:
        manifest["stages"].append(
            run_stage(
                "build_skyguard52_editor_attempt06",
                build_tool,
                [
                    "Skyguard52Editor",
                    "Win64",
                    "Development",
                    f"-Project={project}",
                    "-WaitMutex",
                    "-NoHotReload",
                ],
                logs_root,
                root,
                args.build_timeout,
            )
        )
        save_json(manifest_path, manifest)
        manifest["stages"].append(
            run_stage(
                "author_immutable_candidate_attempt06",
                editor_cmd,
                [
                    str(project),
                    "-run=pythonscript",
                    f"-script={scripts['author']}",
                    "-unattended",
                    "-nop4",
                    "-NoSplash",
                    "-NullRHI",
                ],
                logs_root,
                root,
                args.editor_timeout,
            )
        )
        if not all(path.is_file() for path in output_paths.values()):
            raise RuntimeError("Attempt06 authoring outputs are incomplete")
        manifest["candidate_hashes_before_evidence"] = {
            name: sha256_file(path)
            for name, path in output_paths.items()
        }
        save_json(manifest_path, manifest)
        manifest["stages"].append(
            run_stage(
                "verify_immutable_candidate_attempt06",
                editor_cmd,
                [
                    str(project),
                    "-run=pythonscript",
                    f"-script={scripts['editor_verify']}",
                    "-unattended",
                    "-nop4",
                    "-NoSplash",
                    "-NullRHI",
                ],
                logs_root,
                root,
                args.editor_timeout,
            )
        )
        for mode, map_path in (
            ("baseline", baseline_map),
            ("candidate", candidate_map),
        ):
            output_root = captures_root / mode
            manifest["stages"].append(
                run_stage(
                    f"{mode}_capture_attempt06",
                    editor,
                    [
                        str(project),
                        map_path,
                        f"-ExecutePythonScript={scripts['capture']}",
                        "-ScriptErrorsAreFatal",
                        f"-SkyguardReviewMode={mode}",
                        f"-SkyguardReviewMap={map_path}",
                        f"-SkyguardReviewOutput={output_root}",
                        "-unattended",
                        "-nop4",
                        "-NoSplash",
                        "-RenderOffscreen",
                        "-windowed",
                        "-ResX=1920",
                        "-ResY=1080",
                        "-d3d12",
                        "-sm6",
                    ],
                    logs_root,
                    root,
                    args.editor_timeout,
                )
            )
            expected = 5 if mode == "baseline" else 12
            if not capture_manifest_pass(
                output_root / "capture_manifest.json", expected
            ):
                raise RuntimeError(
                    f"{mode} Attempt06 capture manifest failed"
                )
            save_json(manifest_path, manifest)
        for mode, map_path in (
            ("baseline", baseline_map),
            ("candidate", candidate_map),
        ):
            before = csv_files(root)
            started_epoch = time.time()
            receipt = Path(
                manifest["artifacts"][f"{mode}_profile_receipt"]
            )
            manifest["stages"].append(
                run_stage(
                    f"{mode}_profile_measured_attempt06",
                    editor,
                    [
                        str(project),
                        map_path,
                        "-game",
                        "-windowed",
                        "-ResX=1920",
                        "-ResY=1080",
                        "-d3d12",
                        "-sm6",
                        "-NoVSync",
                        "-NoSplash",
                        "-NoLoadingScreen",
                        (
                            "-ExecCmds=r.SetRes 1920x1080w,"
                            "r.ScreenPercentage 100,"
                            "sg.ViewDistanceQuality 3,"
                            "sg.ShadowQuality 3,"
                            "sg.PostProcessQuality 3,"
                            "sg.TextureQuality 3,"
                            "sg.EffectsQuality 3,"
                            "sg.FoliageQuality 3,"
                            "BugItGo 25200 -8000 10000 -25.226895 90 0"
                        ),
                        "-csvCategories=Global",
                        "-csvGpuStats",
                        "-csvNamedEvents",
                        (
                            "-SkyguardP45ProfileContractId="
                            + contract["contract_id"]
                        ),
                        (
                            "-SkyguardP45ProfileRunId="
                            + attempt_id
                            + "_"
                            + mode
                        ),
                        f"-SkyguardP45ProfileExpectedMap={map_path}",
                        f"-SkyguardP45ProfileReceipt={receipt}",
                        "-SkyguardP45ProfileWarmupSeconds=30",
                        "-SkyguardP45ProfileMeasuredSeconds=60",
                    ],
                    logs_root,
                    root,
                    args.profile_timeout,
                )
            )
            csv_path = newest_new_csv(root, before, started_epoch)
            manifest["artifacts"][f"{mode}_csv"] = str(csv_path)
            profile_receipt = json.loads(
                receipt.read_text(encoding="utf-8-sig")
            )
            if not (
                profile_receipt.get("gate") == "PASS"
                and profile_receipt.get("contract_id")
                == contract["contract_id"]
                and profile_receipt.get(
                    "same_process_warmup_and_measurement"
                )
                is True
                and profile_receipt.get("startup_frames_excluded") is True
                and profile_receipt.get("warmup_seconds") == 30
                and profile_receipt.get("measured_seconds") == 60
            ):
                raise RuntimeError(f"{mode} profile receipt failed")
            save_json(manifest_path, manifest)
        manifest["candidate_hashes_after_evidence"] = {
            name: sha256_file(path)
            for name, path in output_paths.items()
        }
        if (
            manifest["candidate_hashes_after_evidence"]
            != manifest["candidate_hashes_before_evidence"]
        ):
            raise RuntimeError(
                "Attempt06 package hash changed during evidence collection"
            )
        if assert_locked_items(
            root, predecessor["package_hashes"]
        ) != predecessor_packages:
            raise RuntimeError("predecessor package snapshot changed")
        save_json(manifest_path, manifest)
        manifest["stages"].append(
            run_stage(
                "verify_attempt06_visible_gpu_gate",
                Path(sys.executable),
                [
                    str(scripts["gate"]),
                    "--manifest",
                    str(manifest_path),
                    "--output",
                    str(gate_path),
                    "--latest-output",
                    str(latest_gate),
                ],
                logs_root,
                root,
                120,
                accepted_exit_codes=(0, 2),
            )
        )
        gate = json.loads(gate_path.read_text(encoding="utf-8-sig"))
        if gate.get("technical_gate") != "PASS":
            raise RuntimeError("Attempt06 technical gate failed")
        manifest["terminal_state"] = (
            "GATE_COMPLETE"
            if gate.get("gate") == "PASS"
            else "TECHNICAL_GATE_PASS_PENDING_HUMAN_REVIEW"
        )
    except Exception as error:
        manifest["errors"].append(str(error))
        manifest["terminal_state"] = "FAILED"
        raise
    finally:
        manifest["finished_at_utc"] = utc_now()
        try:
            manifest["predecessor_packages_after"] = assert_locked_items(
                root, predecessor["package_hashes"]
            )
        except Exception as lock_error:
            manifest["errors"].append(str(lock_error))
            manifest["terminal_state"] = "FAILED"
        save_json(manifest_path, manifest)
        remaining = wait_for_zero_heavy_processes(30)
        if remaining:
            raise RuntimeError(
                f"heavy processes remain after Attempt06: {remaining}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
