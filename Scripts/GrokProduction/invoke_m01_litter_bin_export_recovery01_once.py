from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil


ROOT = Path(r"D:\Skyguard52")
AUTHORIZATION = ROOT / r"Production\standing_heavy_process_authorization.json"
AUTHORIZATION_BYTES = 2_146
AUTHORIZATION_SHA256 = "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089"
SOURCE = ROOT / r"Production\Attempts\m01-litter-bin-grok-mcp-production01\attempt_20260811T113000000000Z\output\M01_Promenade_LitterBin_Production01.blend"
SOURCE_BYTES = 154_214
SOURCE_SHA256 = "24bbe6acf0f43f86dd14a9bd2750833e89135a6269686974ae56545914014909"
ORIGINAL_GLB = ROOT / r"Production\Attempts\m01-litter-bin-grok-mcp-production01\attempt_20260811T113000000000Z\output\exports\M01_Promenade_LitterBin_Production01.glb"
ORIGINAL_GLB_BYTES = 79_808
ORIGINAL_GLB_SHA256 = "1316256c3bd7a6615df7524048f1db717de5d15fb074cb1b3f394aa40f8c3b38"
ACCEPTANCE = ROOT / r"Docs\AAA_Review\M01_LITTER_BIN_GROK_MCP_PRODUCTION01_ACCEPTANCE_FREEZE.json"
ACCEPTANCE_BYTES = 2_882
ACCEPTANCE_SHA256 = "5d45260b4f8206f13817363e84eba59436b58cb0f2cf3f0961037d2c46de27fc"
STRUCTURE_AUDIT = ROOT / r"Docs\AAA_Review\M01_LITTER_BIN_GROK_MCP_PRODUCTION01_GLB_STRUCTURE_AUDIT.json"
STRUCTURE_AUDIT_BYTES = 1_276
STRUCTURE_AUDIT_SHA256 = "01075c367eb3ad1e22410d5bdfb04a6b5c0386089faa03d64eedef95989c3e34"
SCRIPT = ROOT / r"Scripts\GrokProduction\finalize_m01_litter_bin_export_recovery01_scene.py"
SCRIPT_BYTES = 5_568
SCRIPT_SHA256 = "925e0604c99848f454c39938bc1fc80194cc4dcf7ad5d1022ecce6168d264324"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
BLENDER_BYTES = 112_975_320
BLENDER_SHA256 = "e27fbfea8564aa645d4463cb0949695fd85562b9de6df9561b06859a1074adf7"
ATTEMPT = ROOT / r"Production\Attempts\m01-litter-bin-export-recovery01\attempt_20260811T120000000000Z"
OUTPUT = ATTEMPT / "output"
TERMINAL = ATTEMPT / "terminal_manifest.json"
STDOUT = ATTEMPT / "blender_stdout.log"
STDERR = ATTEMPT / "blender_stderr.log"
PROCESS_SAMPLES = ATTEMPT / "process_tree_samples.jsonl"
EXPECTED_BLEND = OUTPUT / "M01_Promenade_LitterBin_Production01_ExportRecovery01.blend"
EXPECTED_GLB = OUTPUT / "exports" / "M01_Promenade_LitterBin_Production01_ExportRecovery01.glb"
EXPECTED_REPORT = OUTPUT / "export_recovery_report.json"
TIMEOUT_SECONDS = 1_200
REQUIRED_NODES = {
    "SM_M01_Promenade_LitterBin_A",
    "SOCKET_LitterBin_Origin",
    "UCX_SM_M01_Promenade_LitterBin_A_00",
}
HEAVY_NAMES = {
    "blender.exe", "unrealeditor.exe", "unrealeditor-cmd.exe",
    "shadercompileworker.exe", "automationtool.exe", "unrealbuildtool.exe",
    "cl.exe", "link.exe", "dotnet.exe",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path):
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def require_authority(path, size, digest):
    if not path.is_file() or path.stat().st_size != size or sha256(path) != digest:
        raise RuntimeError(f"Authority mismatch: {path}")
    return record(path)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def heavy_processes():
    rows = []
    for process in psutil.process_iter(["pid", "name", "create_time"]):
        try:
            if (process.info.get("name") or "").lower() in HEAVY_NAMES:
                rows.append(process.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return rows


def sample_tree(pid):
    rows = []
    try:
        root = psutil.Process(pid)
        candidates = [root] + root.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        candidates = []
    for process in candidates:
        try:
            rows.append({
                "pid": process.pid,
                "parent_pid": process.ppid(),
                "name": process.name(),
                "working_set": process.memory_info().rss,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    with PROCESS_SAMPLES.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"at_utc": utc_now(), "processes": rows}) + "\n")


def glb_nodes(path):
    with open(path, "rb") as stream:
        magic, version, total = struct.unpack("<4sII", stream.read(12))
        if magic != b"glTF" or version != 2 or total != path.stat().st_size:
            raise RuntimeError("Invalid recovery GLB header")
        length, chunk_type = struct.unpack("<II", stream.read(8))
        if chunk_type != 0x4E4F534A:
            raise RuntimeError("Recovery GLB JSON chunk absent")
        document = json.loads(stream.read(length).decode("utf-8").rstrip("\x00 \t\r\n"))
    return {str(row.get("name", "")) for row in document.get("nodes", [])}


def main():
    started = utc_now()
    process = None
    stdout_handle = None
    stderr_handle = None
    classification = "FAILED_WITH_EVIDENCE"
    failure_stage = "preflight"
    failure_message = None
    timed_out = False
    exit_code = None
    authorities = []
    arguments = []
    source_after = None
    try:
        authorities.extend([
            require_authority(AUTHORIZATION, AUTHORIZATION_BYTES, AUTHORIZATION_SHA256),
            require_authority(SOURCE, SOURCE_BYTES, SOURCE_SHA256),
            require_authority(ORIGINAL_GLB, ORIGINAL_GLB_BYTES, ORIGINAL_GLB_SHA256),
            require_authority(ACCEPTANCE, ACCEPTANCE_BYTES, ACCEPTANCE_SHA256),
            require_authority(STRUCTURE_AUDIT, STRUCTURE_AUDIT_BYTES, STRUCTURE_AUDIT_SHA256),
            require_authority(SCRIPT, SCRIPT_BYTES, SCRIPT_SHA256),
            require_authority(BLENDER, BLENDER_BYTES, BLENDER_SHA256),
        ])
        authorization = json.loads(AUTHORIZATION.read_text(encoding="utf-8"))
        if authorization.get("status") != "ACTIVE" or authorization.get("execution_policy", {}).get("per_run_user_authorization_required") is not False:
            raise RuntimeError("Standing heavy-process authorization is not active")
        if ATTEMPT.exists():
            raise RuntimeError(f"Fresh recovery namespace exists: {ATTEMPT}")
        active = heavy_processes()
        if active:
            raise RuntimeError(f"Heavy process gate failed: {active}")
        ATTEMPT.mkdir(parents=True, exist_ok=False)
        stdout_handle = STDOUT.open("wb")
        stderr_handle = STDERR.open("wb")
        arguments = [str(BLENDER), "--background", str(SOURCE), "--python", str(SCRIPT)]
        failure_stage = "single_blender_export_recovery"
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
                process.kill()
                process.wait(timeout=20)
                raise RuntimeError(f"Blender exceeded {TIMEOUT_SECONDS} seconds")
            time.sleep(0.5)
        process.wait()
        exit_code = int(process.returncode)
        stdout_handle.close()
        stderr_handle.close()
        if exit_code != 0:
            raise RuntimeError(f"Blender returned exit code {exit_code}")
        failure_stage = "postflight"
        for path in (EXPECTED_BLEND, EXPECTED_GLB, EXPECTED_REPORT):
            if not path.is_file():
                raise RuntimeError(f"Required recovery output missing: {path}")
        report = json.loads(EXPECTED_REPORT.read_text(encoding="utf-8"))
        if report.get("classification") != "PASSED_GLTF_STRUCTURE_READY_FOR_UNREAL_STAGING":
            raise RuntimeError(f"Unexpected recovery report: {report.get('classification')}")
        nodes = glb_nodes(EXPECTED_GLB)
        if not REQUIRED_NODES.issubset(nodes):
            raise RuntimeError(f"Recovery GLB lacks governed nodes: {sorted(nodes)}")
        source_after = record(SOURCE)
        if source_after["bytes"] != SOURCE_BYTES or source_after["sha256"] != SOURCE_SHA256:
            raise RuntimeError("Accepted source blend changed")
        classification = "PASSED_GLTF_STRUCTURE_READY_FOR_UNREAL_STAGING"
        failure_stage = None
    except Exception as exc:
        failure_message = f"{type(exc).__name__}: {exc}"
    finally:
        if stdout_handle is not None and not stdout_handle.closed:
            stdout_handle.close()
        if stderr_handle is not None and not stderr_handle.closed:
            stderr_handle.close()
        if source_after is None and SOURCE.is_file():
            source_after = record(SOURCE)
        if ATTEMPT.exists():
            artifacts = [record(path) for path in sorted(item for item in ATTEMPT.rglob("*") if item.is_file() and item != TERMINAL)]
            write_json(TERMINAL, {
                "schema": "skyguard.m01-litter-bin.export-recovery01.terminal.v1",
                "classification": classification,
                "started_at_utc": started,
                "ended_at_utc": utc_now(),
                "failure_stage": failure_stage,
                "failure_message": failure_message,
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
                "authorities": authorities,
                "source_after": source_after,
                "artifacts": artifacts,
                "runtime_promotion_performed": False,
                "next_gate": "Fresh isolated Unreal staging import" if classification.startswith("PASSED_") else "Preserve failure; never retry this namespace",
            })
    print(classification)
    return 0 if classification.startswith("PASSED_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
