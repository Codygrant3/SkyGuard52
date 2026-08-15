from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil


ROOT = Path(r"D:\Skyguard52")
ISOLATED = Path(r"D:\SG52T08_ENV01")
AUTHORIZATION = ROOT / "Production" / "standing_heavy_process_authorization.json"
AUTHORIZATION_BYTES = 2_146
AUTHORIZATION_SHA256 = "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089"
AUTHOR = ROOT / r"Scripts\GrokProduction\validate_m01_utility_cabinet_recovery04_unreal_integration01_recovery01.py"
AUTHOR_BYTES = 13_066
AUTHOR_SHA256 = "8c39b54bdba679c5e559f5956845a85ebc7249bca72abdbca1c5ec8e5fa2d076"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA256 = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
INPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01.umap"
INPUT_MAP_BYTES = 765_110
INPUT_MAP_SHA256 = "1a1636e225d8192309e62b5da4c4df7e7b7adffbcc2a3fc65c8cd8372c6cdc3c"
OUTPUT_MAP = ISOLATED / "Content/M01/Lvl_M01_PhotorealFoundation_CoastalCorridorC06R01Recovery01_PromenadeBollards01_BicycleRacks01_UtilityCabinets01Recovery01.umap"
EDITOR = Path(r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe")
EDITOR_BYTES = 512_952
EDITOR_SHA256 = "0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0"
ATTEMPT = ROOT / r"Saved\BuildAttempts\M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01_RECOVERY01\attempt_01"
RECEIPT = ATTEMPT / "validation_receipt.json"
TERMINAL = ROOT / r"Saved\Reports\M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01_RECOVERY01_TERMINAL_SUPERVISOR.json"
TIMEOUT_SECONDS = 1_800

HEAVY_NAMES = {
    "blender.exe", "unrealeditor.exe", "unrealeditor-cmd.exe", "shadercompileworker.exe",
    "automationtool.exe", "unrealbuildtool.exe", "cl.exe", "link.exe", "dotnet.exe",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def require_authority(path: Path, size: int, digest: str) -> dict[str, object]:
    if not path.is_file() or path.stat().st_size != size or sha256(path) != digest:
        raise RuntimeError(f"Authority mismatch: {path}")
    return record(path)


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite terminal evidence: {path}")
    temporary.replace(path)


def heavy_processes() -> list[dict[str, object]]:
    rows = []
    for process in psutil.process_iter(["pid", "name", "create_time"]):
        try:
            if (process.info.get("name") or "").lower() in HEAVY_NAMES:
                rows.append(process.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return rows


def sample_tree(process: subprocess.Popen[bytes], destination: Path) -> None:
    rows = []
    try:
        root = psutil.Process(process.pid)
        candidates = [root] + root.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        candidates = []
    for candidate in candidates:
        try:
            rows.append({"pid": candidate.pid, "parent_pid": candidate.ppid(), "name": candidate.name(), "working_set": candidate.memory_info().rss})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    with destination.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"at_utc": utc_now(), "processes": rows}) + "\n")


def main() -> int:
    started = utc_now()
    process = None
    stdout_handle = None
    stderr_handle = None
    classification = "FAILED_WITH_EVIDENCE"
    failure_stage = "preflight"
    failure_message = None
    exit_code = None
    exit_code_type = None
    timed_out = False
    unreal_launches = 0
    authorities = []
    arguments: list[str] = []
    process_samples = ATTEMPT / "process_tree_samples.jsonl"

    try:
        authorities.extend([
            require_authority(AUTHORIZATION, AUTHORIZATION_BYTES, AUTHORIZATION_SHA256),
            require_authority(AUTHOR, AUTHOR_BYTES, AUTHOR_SHA256),
            require_authority(PROJECT, PROJECT_BYTES, PROJECT_SHA256),
            require_authority(INPUT_MAP, INPUT_MAP_BYTES, INPUT_MAP_SHA256),
            require_authority(EDITOR, EDITOR_BYTES, EDITOR_SHA256),
        ])
        authorization = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))
        if authorization.get("status") != "ACTIVE" or authorization.get("execution_policy", {}).get("per_run_user_authorization_required") is not False:
            raise RuntimeError("Standing heavy-process authorization is not active")
        if ATTEMPT.exists() or TERMINAL.exists() or OUTPUT_MAP.exists():
            raise RuntimeError("Fresh Recovery01 namespace is not absent")
        active = heavy_processes()
        if active:
            raise RuntimeError(f"Heavy process gate failed: {active}")
        offline = subprocess.run([sys.executable, str(AUTHOR), "--offline-contract-test"], cwd=str(ROOT), capture_output=True, text=True, timeout=60, check=False)
        if offline.returncode != 0 or "PASS_M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01_RECOVERY01_CONTRACT" not in offline.stdout:
            raise RuntimeError(f"Author offline contract failed: {offline.stdout} {offline.stderr}")

        ATTEMPT.mkdir(parents=True, exist_ok=False)
        stdout_path = ATTEMPT / "unreal.stdout.log"
        stderr_path = ATTEMPT / "unreal.stderr.log"
        engine_log = ATTEMPT / "unreal.engine.log"
        arguments = [
            str(PROJECT), "-run=pythonscript", f"-script={AUTHOR}", "-unattended", "-nop4", "-nosplash",
            "-nullrhi", "-NoSound", "-stdout", "-FullStdOutLogOutput", f"-abslog={engine_log}",
            "-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared",
            "-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False",
        ]
        stdout_handle = (ATTEMPT / "unreal.stdout.log").open("wb")
        stderr_handle = (ATTEMPT / "unreal.stderr.log").open("wb")
        failure_stage = "launch"
        process = subprocess.Popen([str(EDITOR), *arguments], cwd=str(ROOT), stdout=stdout_handle, stderr=stderr_handle)
        unreal_launches = 1
        failure_stage = "wait"
        deadline = time.monotonic() + TIMEOUT_SECONDS
        next_sample = 0.0
        while process.poll() is None:
            now = time.monotonic()
            if now >= next_sample:
                sample_tree(process, process_samples)
                next_sample = now + 5.0
            if now >= deadline:
                timed_out = True
                process.kill()
                process.wait(timeout=20)
                raise RuntimeError(f"Unreal Recovery01 exceeded {TIMEOUT_SECONDS} seconds")
            time.sleep(1.0)
        process.wait()
        exit_code = int(process.returncode)
        exit_code_type = "System.Int32"
        if exit_code != 0:
            raise RuntimeError(f"Unreal returned exit code {exit_code}")

        failure_stage = "postflight"
        if not RECEIPT.is_file():
            raise RuntimeError("Recovery01 validation receipt is missing")
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        expected = "PASSED_M01_UTILITY_CABINET_RECOVERY04_UNREAL_INTEGRATION01_RECOVERY01_READY_FOR_D3D12_VISUAL_PROOF"
        if receipt.get("classification") != expected:
            raise RuntimeError(f"Unexpected receipt classification: {receipt.get('classification')} error={receipt.get('error')}")
        if len(receipt.get("cabinet_actors", [])) != 5 or receipt.get("accepted_inputs_mutated") is not False:
            raise RuntimeError("Recovery01 cabinet validation contract failed")
        if not OUTPUT_MAP.is_file() or sha256(INPUT_MAP) != INPUT_MAP_SHA256:
            raise RuntimeError("Recovery01 output/source-map contract failed")
        engine_text = (ATTEMPT / "unreal.engine.log").read_text(encoding="utf-8", errors="replace")
        if "Invalid input SpecularColorFactor" in engine_text:
            raise RuntimeError("Interchange material error recurred despite no-import recovery")
        classification = expected
        failure_stage = None
    except Exception as exc:
        failure_message = f"{type(exc).__name__}: {exc}"
    finally:
        if stdout_handle is not None and not stdout_handle.closed:
            stdout_handle.close()
        if stderr_handle is not None and not stderr_handle.closed:
            stderr_handle.close()
        artifacts = []
        if ATTEMPT.exists():
            for path in sorted(item for item in ATTEMPT.rglob("*") if item.is_file()):
                artifacts.append(record(path))
        terminal = {
            "schema": "skyguard.m01-utility-cabinet-recovery04.unreal-integration01-recovery01.supervisor.v1",
            "classification": classification,
            "started_at_utc": started,
            "ended_at_utc": utc_now(),
            "failure_stage": failure_stage,
            "failure_message": failure_message,
            "execution": {"supervisor_launches": 1, "unreal_launches": unreal_launches, "blender_launches": 0, "retries": 0, "timed_out": timed_out, "pid": process.pid if process else None, "exit_code": exit_code, "exit_code_type": exit_code_type},
            "exact_executable": str(EDITOR),
            "exact_arguments": arguments,
            "authorities": authorities,
            "receipt": record(RECEIPT) if RECEIPT.is_file() else None,
            "output_map": record(OUTPUT_MAP) if OUTPUT_MAP.is_file() else None,
            "attempt_artifacts": artifacts,
            "accepted_input_map_unchanged": bool(INPUT_MAP.is_file() and sha256(INPUT_MAP) == INPUT_MAP_SHA256),
            "next_gate": "Use this clean map as the base for subsequent accepted environment-prop integration" if classification.startswith("PASSED_") else "Preserve failure evidence; never retry this namespace",
        }
        try:
            write_json_atomic(TERMINAL, terminal)
        except Exception as exc:
            print(f"TERMINAL_WRITE_FAILURE: {exc}", file=sys.stderr)
            classification = "FAILED_WITH_EVIDENCE"

    print(classification)
    return 0 if classification.startswith("PASSED_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
