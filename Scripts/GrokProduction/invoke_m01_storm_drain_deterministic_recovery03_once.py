from __future__ import annotations

import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil
from PIL import Image


ROOT = Path(r"D:\Skyguard52")
AUTHORIZATION = ROOT / "Production" / "standing_heavy_process_authorization.json"
AUTHORIZATION_BYTES = 2_146
AUTHORIZATION_SHA256 = "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089"
SOURCE = ROOT / r"Production\Attempts\m01-storm-drain-grok-mcp-recovery01\attempt_20260811T101500000000Z\output\checkpoint\M01_Promenade_StormDrain_Recovery01_Checkpoint.blend"
SOURCE_BYTES = 189_507
SOURCE_SHA256 = "f1ea5dde0822673f347026cd818ac8afa668f78d2ff4defabea87a9d360785e2"
PRIOR_FAILURE_FREEZE = ROOT / r"Docs\AAA_Review\M01_STORM_DRAIN_DETERMINISTIC_RECOVERY02_ATTEMPT01_TERMINAL_FREEZE.json"
PRIOR_FAILURE_FREEZE_BYTES = 3_005
PRIOR_FAILURE_FREEZE_SHA256 = "37484b33737ce3d0ed9ea92b95a03604569c3f4c4c7ee2da37481d3a6c1ace38"
SCRIPT = ROOT / r"Scripts\GrokProduction\finalize_m01_storm_drain_deterministic_recovery03_scene.py"
SCRIPT_BYTES = 3_297
SCRIPT_SHA256 = "174ad1ee4d7e9c84d685c00128f6c77557b82a90e8f9d4632066dbf4abcf4b48"
ATTEMPT = ROOT / r"Production\Attempts\m01-storm-drain-deterministic-recovery03\attempt_20260811T104500000000Z"
OUTPUT = ATTEMPT / "output"
TERMINAL = ATTEMPT / "terminal_manifest.json"
STDOUT = ATTEMPT / "blender_stdout.log"
STDERR = ATTEMPT / "blender_stderr.log"
PROCESS_SAMPLES = ATTEMPT / "process_tree_samples.jsonl"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
BLENDER_BYTES = 112_975_320
BLENDER_SHA256 = "e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7"
EXPECTED_BLEND = OUTPUT / "M01_Promenade_StormDrain_Recovery03.blend"
EXPECTED_GLB = OUTPUT / "exports" / "M01_Promenade_StormDrain_Recovery03.glb"
EXPECTED_REPORT = OUTPUT / "grok_implementation_report.json"
TIMEOUT_SECONDS = 1_200
HEAVY_NAMES = {
    "blender.exe",
    "unrealeditor.exe",
    "unrealeditor-cmd.exe",
    "shadercompileworker.exe",
    "automationtool.exe",
    "unrealbuildtool.exe",
    "cl.exe",
    "link.exe",
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


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def heavy_processes() -> list[dict[str, object]]:
    rows = []
    for process in psutil.process_iter(["pid", "name", "create_time"]):
        try:
            if (process.info.get("name") or "").lower() in HEAVY_NAMES:
                rows.append(process.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return rows


def sample_tree(pid: int) -> None:
    rows = []
    try:
        root = psutil.Process(pid)
        candidates = [root] + root.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        candidates = []
    for process in candidates:
        try:
            rows.append(
                {
                    "pid": process.pid,
                    "parent_pid": process.ppid(),
                    "name": process.name(),
                    "working_set": process.memory_info().rss,
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    with PROCESS_SAMPLES.open("a", encoding="utf-8") as stream:
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
    timed_out = False
    authorities: list[dict[str, object]] = []
    source_after = None
    arguments: list[str] = []
    try:
        authorities.extend(
            [
                require_authority(AUTHORIZATION, AUTHORIZATION_BYTES, AUTHORIZATION_SHA256),
                require_authority(SOURCE, SOURCE_BYTES, SOURCE_SHA256),
                require_authority(PRIOR_FAILURE_FREEZE, PRIOR_FAILURE_FREEZE_BYTES, PRIOR_FAILURE_FREEZE_SHA256),
                require_authority(SCRIPT, SCRIPT_BYTES, SCRIPT_SHA256),
                require_authority(BLENDER, BLENDER_BYTES, BLENDER_SHA256),
            ]
        )
        authorization = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))
        if authorization.get("status") != "ACTIVE" or authorization.get("execution_policy", {}).get("per_run_user_authorization_required") is not False:
            raise RuntimeError("Standing heavy-process authorization is not active")
        if ATTEMPT.exists():
            raise RuntimeError(f"Fresh deterministic recovery namespace exists: {ATTEMPT}")
        active = heavy_processes()
        if active:
            raise RuntimeError(f"Heavy process gate failed: {active}")
        ATTEMPT.mkdir(parents=True, exist_ok=False)
        stdout_handle = STDOUT.open("wb")
        stderr_handle = STDERR.open("wb")
        arguments = [str(BLENDER), "--background", str(SOURCE), "--python", str(SCRIPT)]
        failure_stage = "single_blender_finalization"
        process = subprocess.Popen(arguments, cwd=str(ROOT), stdout=stdout_handle, stderr=stderr_handle)
        deadline = time.monotonic() + TIMEOUT_SECONDS
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
            raise RuntimeError(f"Blender deterministic recovery failed: exit={exit_code}, timed_out={timed_out}")

        failure_stage = "automatic_postflight"
        for required in (EXPECTED_BLEND, EXPECTED_GLB, EXPECTED_REPORT):
            if not required.is_file():
                raise RuntimeError(f"Required output is missing: {required}")
        report = json.loads(EXPECTED_REPORT.read_text(encoding="utf-8"))
        if report.get("classification") != "PASSED_AWAITING_DIRECT_VISUAL_REVIEW" or report.get("slot_count") != 12:
            raise RuntimeError(
                f"Unexpected implementation report: {report.get('classification')} slots={report.get('slot_count')}"
            )
        renders = sorted((OUTPUT / "renders").glob("*.png"))
        if len(renders) != 8:
            raise RuntimeError(f"Expected exactly eight renders, found {len(renders)}")
        for path in renders:
            with Image.open(path) as image:
                if image.size != (1920, 1080):
                    raise RuntimeError(f"Wrong render dimensions: {path} {image.size}")
        source_after = record(SOURCE)
        if source_after["bytes"] != SOURCE_BYTES or source_after["sha256"] != SOURCE_SHA256:
            raise RuntimeError("Frozen Grok checkpoint changed")
        classification = "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW"
        failure_stage = None
    except Exception as exc:
        failure_message = f"{type(exc).__name__}: {exc}"
    finally:
        if stdout_handle is not None and not stdout_handle.closed:
            stdout_handle.close()
        if stderr_handle is not None and not stderr_handle.closed:
            stderr_handle.close()
        if SOURCE.is_file() and source_after is None:
            source_after = record(SOURCE)
        if ATTEMPT.exists():
            inventory = [
                record(path)
                for path in sorted(item for item in ATTEMPT.rglob("*") if item.is_file() and item != TERMINAL)
            ]
            write_json(
                TERMINAL,
                {
                    "schema": "skyguard.m01-storm-drain.deterministic-recovery03.terminal.v1",
                    "created_at_utc": utc_now(),
                    "started_at_utc": started,
                    "classification": classification,
                    "failure_stage": failure_stage,
                    "failure_message": failure_message,
                    "attempt_root": str(ATTEMPT),
                    "authorities": authorities,
                    "source_authority": {
                        "expected_bytes": SOURCE_BYTES,
                        "expected_sha256": SOURCE_SHA256,
                        "after": source_after,
                    },
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
                    "exact_arguments": arguments,
                    "artifacts": inventory,
                    "runtime_promotion_performed": False,
                    "next_gate": (
                        "Direct full-resolution review of all eight original renders"
                        if classification.startswith("PASSED_")
                        else "Preserve failure; never retry this namespace"
                    ),
                },
            )
    print(classification)
    return 0 if classification.startswith("PASSED_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
