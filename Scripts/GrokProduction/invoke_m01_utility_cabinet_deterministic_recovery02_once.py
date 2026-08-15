from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil
from PIL import Image


PROJECT = Path(r"D:\Skyguard52")
AUTHORITY = PROJECT / "Production" / "standing_heavy_process_authorization.json"
AUTHORITY_BYTES = 2146
AUTHORITY_SHA = "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089"
SOURCE = PROJECT / "Production" / "Attempts" / "m01-street-detail-kit-finalizer-recovery01" / "attempt_20260811T071500000000Z" / "output" / "M01_StreetDetailKit_GrokMCP_Production_A.blend"
SOURCE_BYTES = 494714
SOURCE_SHA = "cf0d2b275d1299e686fb1e772e6d35db0ae099b3a255661061427679ef8c0bba"
PRIOR_FREEZE = PROJECT / "Docs" / "AAA_Review" / "M01_UTILITY_CABINET_GROK_MCP_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json"
PRIOR_FREEZE_BYTES = 2749
PRIOR_FREEZE_SHA = "2762c34ab17e1349c9876c1b145e0eedd0f695bfaa5771460d5fb0c02874f4c0"
SCRIPT = PROJECT / "Scripts" / "GrokProduction" / "recover_m01_utility_cabinet_recovery02_scene.py"
ATTEMPT = PROJECT / "Production" / "Attempts" / "m01-utility-cabinet-deterministic-recovery02" / "attempt_20260811T093000000000Z"
OUTPUT = ATTEMPT / "output"
TERMINAL = ATTEMPT / "terminal_manifest.json"
STDOUT = ATTEMPT / "blender_stdout.log"
STDERR = ATTEMPT / "blender_stderr.log"
PROCESS_SAMPLES = ATTEMPT / "process_tree_samples.jsonl"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
EXPECTED_BLEND = OUTPUT / "M01_Promenade_UtilityCabinet_Recovery02.blend"
EXPECTED_GLB = OUTPUT / "exports" / "M01_Promenade_UtilityCabinet_Recovery02.glb"
EXPECTED_REPORT = OUTPUT / "implementation_report.json"
HEAVY_NAMES = {"blender.exe", "unrealeditor.exe", "unrealeditor-cmd.exe", "shadercompileworker.exe", "automationtool.exe", "unrealbuildtool.exe", "cl.exe", "link.exe"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def require(path: Path, size: int | None = None, digest: str | None = None) -> None:
    if not path.is_file():
        raise RuntimeError(f"Missing authority: {path}")
    if size is not None and path.stat().st_size != size:
        raise RuntimeError(f"Byte mismatch: {path}")
    if digest is not None and sha256(path) != digest:
        raise RuntimeError(f"SHA-256 mismatch: {path}")


def heavy_processes() -> list[dict]:
    rows = []
    for process in psutil.process_iter(["pid", "name", "create_time"]):
        try:
            if (process.info.get("name") or "").lower() in HEAVY_NAMES:
                rows.append(process.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return rows


def sample_tree(root_pid: int) -> None:
    rows = []
    try:
        root = psutil.Process(root_pid)
        candidates = [root] + root.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        candidates = []
    for process in candidates:
        try:
            rows.append({"pid": process.pid, "parent_pid": process.ppid(), "name": process.name()})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    with PROCESS_SAMPLES.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"at_utc": utc_now(), "processes": rows}) + "\n")


def main() -> int:
    started = utc_now()
    process = None
    stdout_handle = None
    stderr_handle = None
    exit_code = None
    timed_out = False
    classification = "FAILED_WITH_EVIDENCE"
    failure_stage = "preflight"
    failure_message = None
    source_after = None
    try:
        require(AUTHORITY, AUTHORITY_BYTES, AUTHORITY_SHA)
        require(SOURCE, SOURCE_BYTES, SOURCE_SHA)
        require(PRIOR_FREEZE, PRIOR_FREEZE_BYTES, PRIOR_FREEZE_SHA)
        require(SCRIPT)
        require(BLENDER)
        if ATTEMPT.exists():
            raise RuntimeError(f"Fresh attempt namespace already exists: {ATTEMPT}")
        active = heavy_processes()
        if active:
            raise RuntimeError(f"Governed heavy process already active: {active}")
        ATTEMPT.mkdir(parents=True, exist_ok=False)
        failure_stage = "single_blender_recovery_launch"
        stdout_handle = STDOUT.open("wb")
        stderr_handle = STDERR.open("wb")
        arguments = [str(BLENDER), "--background", str(SOURCE), "--python", str(SCRIPT)]
        process = subprocess.Popen(arguments, cwd=str(PROJECT), stdout=stdout_handle, stderr=stderr_handle)
        deadline = time.monotonic() + 20 * 60
        next_sample = 0.0
        while process.poll() is None:
            now = time.monotonic()
            if now >= next_sample:
                sample_tree(process.pid)
                next_sample = now + 5.0
            if now >= deadline:
                timed_out = True
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
                break
            time.sleep(0.5)
        process.wait()
        exit_code = int(process.returncode)
        stdout_handle.close()
        stderr_handle.close()
        if timed_out or exit_code != 0:
            raise RuntimeError(f"Blender recovery failed or timed out: exit={exit_code}, timed_out={timed_out}")
        failure_stage = "automatic_postflight"
        for required in (EXPECTED_BLEND, EXPECTED_GLB, EXPECTED_REPORT):
            require(required)
        report = json.loads(EXPECTED_REPORT.read_text(encoding="utf-8"))
        if report.get("classification") != "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW":
            raise RuntimeError(f"Unexpected report classification: {report.get('classification')}")
        renders = sorted((OUTPUT / "checkpoint").glob("*.png"))
        if len(renders) != 8:
            raise RuntimeError(f"Expected exactly eight checkpoint renders, found {len(renders)}")
        for path in renders:
            with Image.open(path) as image:
                if image.size != (1920, 1080):
                    raise RuntimeError(f"Wrong render dimensions for {path}: {image.size}")
        source_after = record(SOURCE)
        if source_after["bytes"] != SOURCE_BYTES or source_after["sha256"] != SOURCE_SHA:
            raise RuntimeError("Immutable source blend changed")
        classification = "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW"
        failure_stage = None
    except Exception as exc:
        failure_message = str(exc)
    finally:
        if stdout_handle is not None and not stdout_handle.closed:
            stdout_handle.close()
        if stderr_handle is not None and not stderr_handle.closed:
            stderr_handle.close()
        if SOURCE.is_file() and source_after is None:
            source_after = record(SOURCE)
        if ATTEMPT.exists():
            inventory = [record(path) for path in sorted(item for item in ATTEMPT.rglob("*") if item.is_file() and item != TERMINAL)]
            write_json(TERMINAL, {
                "schema": "skyguard.m01-utility-cabinet.deterministic-recovery02.terminal.v1",
                "created_at_utc": utc_now(),
                "started_at_utc": started,
                "classification": classification,
                "failure_stage": failure_stage,
                "failure_message": failure_message,
                "attempt_root": str(ATTEMPT),
                "source_authority": {"expected_bytes": SOURCE_BYTES, "expected_sha256": SOURCE_SHA, "after": source_after},
                "prior_failure_freeze": record(PRIOR_FREEZE),
                "recovery_script": record(SCRIPT),
                "execution": {
                    "blender_launches": 1 if process else 0,
                    "grok_launches": 0,
                    "unreal_launches": 0,
                    "retries": 0,
                    "timed_out": timed_out,
                    "pid": process.pid if process else None,
                    "exit_code": exit_code,
                    "exit_code_type": "System.Int32" if exit_code is not None else None,
                },
                "artifacts": inventory,
                "runtime_promotion_performed": False,
                "next_gate": "Direct review of all eight original checkpoint renders." if classification != "FAILED_WITH_EVIDENCE" else "Preserve failure and do not retry this namespace.",
            })
    print(classification)
    return 0 if classification != "FAILED_WITH_EVIDENCE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
