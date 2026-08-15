"""One-shot supervisor for the accepted Igla missile Unreal staging import."""

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
AUTHORIZATION_SHA = "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089"
AUTHOR = ROOT / "Scripts/GrokProduction/author_core_igla_missile_refinement01_unreal_integration01.py"
ACCEPTANCE = ROOT / "Docs/AAA_Review/CORE_IGLA_MISSILE_GROK_MCP_REFINEMENT01_ACCEPTANCE_FREEZE.json"
ACCEPTANCE_BYTES = 2_952
ACCEPTANCE_SHA = "9c9cc2a4b48522fe3dd5fc0cbe5421047c4e209982f2e9c2a50700b2c390adcc"
SOURCE = ROOT / r"Production\Attempts\core-igla-missile-grok-mcp-refinement01\attempt_20260811T0737000000000Z\output\exports\CORE_IglaMissile_Refinement01.glb"
SOURCE_BYTES = 1_079_028
SOURCE_SHA = "f17b665bd8f7a88fc05d9a925e910c0a74fa43b5c4f3a87c28446f7a581ea497"
PROJECT = ISOLATED / "Skyguard52.uproject"
PROJECT_BYTES = 3_703
PROJECT_SHA = "7043de4d029b9927301c0adfc4bbf4fc9f4e7790f02c4321138fe4da2d034e5a"
DESTINATION = ISOLATED / "Content/Skyguard/Combat/Weapons/IglaMissileRefinement01"
OUTPUT_MAP = DESTINATION / "Lvl_CORE_IglaMissile_Refinement01_ImportAudit.umap"
ATTEMPT = ROOT / "Saved/BuildAttempts/CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_INTEGRATION01/attempt_01"
RECEIPT = ATTEMPT / "integration_receipt.json"
TERMINAL = ROOT / "Saved/Reports/CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_INTEGRATION01_TERMINAL_SUPERVISOR.json"
EDITOR = Path(r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe")
EDITOR_BYTES = 512_952
EDITOR_SHA = "0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0"
TIMEOUT_SECONDS = 1_800

HEAVY_NAMES = {
    "blender.exe",
    "unrealeditor.exe",
    "unrealeditor-cmd.exe",
    "shadercompileworker.exe",
    "automationtool.exe",
    "unrealbuildtool.exe",
    "cl.exe",
    "link.exe",
    "dotnet.exe",
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


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite terminal evidence: {path}")
    temporary.replace(path)


def require_authority(path: Path, size: int, digest: str) -> dict[str, object]:
    if not path.is_file() or path.stat().st_size != size or sha256(path) != digest:
        raise RuntimeError(f"Authority mismatch: {path}")
    return record(path)


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
            rows.append(
                {
                    "pid": candidate.pid,
                    "parent_pid": candidate.ppid(),
                    "name": candidate.name(),
                    "working_set": candidate.memory_info().rss,
                    "cpu_seconds": sum(candidate.cpu_times()[:2]),
                }
            )
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
    authorities: list[dict[str, object]] = []
    arguments: list[str] = []
    process_samples = ATTEMPT / "process_tree_samples.jsonl"

    try:
        author_record = record(AUTHOR)
        authorities.extend(
            [
                require_authority(AUTHORIZATION, AUTHORIZATION_BYTES, AUTHORIZATION_SHA),
                author_record,
                require_authority(ACCEPTANCE, ACCEPTANCE_BYTES, ACCEPTANCE_SHA),
                require_authority(SOURCE, SOURCE_BYTES, SOURCE_SHA),
                require_authority(PROJECT, PROJECT_BYTES, PROJECT_SHA),
                require_authority(EDITOR, EDITOR_BYTES, EDITOR_SHA),
            ]
        )
        authorization = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))
        if authorization.get("status") != "ACTIVE" or authorization.get("execution_policy", {}).get("per_run_user_authorization_required") is not False:
            raise RuntimeError("Standing heavy-process authorization is not active")
        if ATTEMPT.exists() or TERMINAL.exists() or OUTPUT_MAP.exists() or DESTINATION.exists():
            raise RuntimeError("Fresh Igla Unreal staging namespace is not absent")
        active = heavy_processes()
        if active:
            raise RuntimeError(f"Heavy process gate failed: {active}")
        offline = subprocess.run(
            [sys.executable, str(AUTHOR), "--offline-contract-test"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if offline.returncode != 0 or "PASS_CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_INTEGRATION01_CONTRACT" not in offline.stdout:
            raise RuntimeError(f"Author offline contract failed: {offline.stdout} {offline.stderr}")

        ATTEMPT.mkdir(parents=True, exist_ok=False)
        stdout_path = ATTEMPT / "unreal.stdout.log"
        stderr_path = ATTEMPT / "unreal.stderr.log"
        engine_log = ATTEMPT / "unreal.engine.log"
        arguments = [
            str(PROJECT),
            "-run=pythonscript",
            f"-script={AUTHOR}",
            "-unattended",
            "-nop4",
            "-nosplash",
            "-nullrhi",
            "-NoSound",
            "-stdout",
            "-FullStdOutLogOutput",
            f"-abslog={engine_log}",
            "-DisablePlugins=Fab,Bridge,EditorTelemetry,RuntimeTelemetry,EOSShared",
            "-ini:EditorSettings:[/Script/UnrealEd.AnalyticsPrivacySettings]:bSendUsageData=False",
        ]
        stdout_handle = stdout_path.open("wb")
        stderr_handle = stderr_path.open("wb")
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
                raise RuntimeError(f"Unreal staging import exceeded {TIMEOUT_SECONDS} seconds")
            time.sleep(1.0)
        process.wait()
        exit_code = int(process.returncode)
        exit_code_type = "System.Int32"
        if exit_code != 0:
            raise RuntimeError(f"Unreal returned exit code {exit_code}")

        failure_stage = "postflight"
        if not RECEIPT.is_file():
            raise RuntimeError("Integration receipt is missing")
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        expected = "PASSED_CORE_IGLA_MISSILE_REFINEMENT01_UNREAL_STAGING_READY_FOR_D3D12_VISUAL_PROOF"
        if receipt.get("classification") != expected:
            raise RuntimeError(f"Unexpected receipt classification: {receipt.get('classification')} error={receipt.get('error')}")
        if len(receipt.get("placements", [])) != 3:
            raise RuntimeError("Igla audit placement contract failed")
        if not OUTPUT_MAP.is_file() or not DESTINATION.is_dir():
            raise RuntimeError("Expected fresh Unreal outputs are absent")
        if sha256(SOURCE) != SOURCE_SHA or sha256(ACCEPTANCE) != ACCEPTANCE_SHA or sha256(PROJECT) != PROJECT_SHA:
            raise RuntimeError("Accepted authority changed during integration")
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
            artifacts = [record(path) for path in sorted(ATTEMPT.rglob("*")) if path.is_file()]
        terminal = {
            "schema": "skyguard.core-igla-missile-refinement01.unreal-integration01.supervisor.v1",
            "classification": classification,
            "started_at_utc": started,
            "ended_at_utc": utc_now(),
            "failure_stage": failure_stage,
            "failure_message": failure_message,
            "execution": {
                "supervisor_launches": 1,
                "unreal_launches": unreal_launches,
                "blender_launches": 0,
                "retries": 0,
                "timed_out": timed_out,
                "pid": process.pid if process else None,
                "exit_code": exit_code,
                "exit_code_type": exit_code_type,
            },
            "exact_executable": str(EDITOR),
            "exact_arguments": arguments,
            "authorities": authorities,
            "receipt": record(RECEIPT) if RECEIPT.is_file() else None,
            "output_map": record(OUTPUT_MAP) if OUTPUT_MAP.is_file() else None,
            "destination_inventory": [record(path) for path in sorted(DESTINATION.rglob("*")) if path.is_file()] if DESTINATION.is_dir() else [],
            "attempt_artifacts": artifacts,
            "accepted_inputs_unchanged": bool(
                SOURCE.is_file()
                and ACCEPTANCE.is_file()
                and PROJECT.is_file()
                and sha256(SOURCE) == SOURCE_SHA
                and sha256(ACCEPTANCE) == ACCEPTANCE_SHA
                and sha256(PROJECT) == PROJECT_SHA
            ),
            "runtime_proxy_replaced": False,
            "next_gate": "D3D12 visual proof of the fresh audit map" if classification.startswith("PASSED_") else "Preserve failure evidence; never retry this namespace",
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
