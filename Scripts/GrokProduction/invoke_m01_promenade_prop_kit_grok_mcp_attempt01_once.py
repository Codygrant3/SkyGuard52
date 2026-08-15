from __future__ import annotations

import hashlib
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil
from PIL import Image


PROJECT = Path(r"D:\Skyguard52")
AUTHORITY = PROJECT / "Production" / "standing_heavy_process_authorization.json"
AUTHORITY_BYTES = 2146
AUTHORITY_SHA = "48277d7edd869cc2b841c3993e8f7599bec5291ddf23e9c442b33e09b870c089"
SOURCE = PROJECT / "Content" / "Skyguard" / "Meshes" / "Source" / "Mission01" / "Coastal_Production_001" / "BLD_M01_COAST_PROD_001_MASTER.blend"
SOURCE_BYTES = 201985
SOURCE_SHA = "4cb6bc2acc06310c4328687d65c808db6adfe5b1c5e49774a81bec60bf4a08cb"
PROMPT = PROJECT / "Production" / "Prompts" / "M01_PROMENADE_PROP_KIT_GROK_MCP_PRODUCTION_ATTEMPT01.md"
FINALIZER = PROJECT / "Scripts" / "GrokProduction" / "finalize_m01_promenade_prop_kit_scene.py"
ATTEMPT = PROJECT / "Production" / "Attempts" / "m01-promenade-prop-kit-grok-mcp" / "attempt_20260811T061500000000Z"
OUTPUT = ATTEMPT / "output"
TERMINAL = ATTEMPT / "terminal_manifest.json"
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
NODE = Path(r"C:\Program Files\nodejs\node.exe")
CODEX = Path(r"C:\Users\chris\AppData\Roaming\npm\node_modules\@openai\codex\bin\codex.js")
ROUTER_SECRET_FILE = Path(r"C:\Users\chris\.codex\codex-router\caller-secret")
MCP_CLIENT = PROJECT / "Tools" / "BlenderMCP" / "skyguard_blender_mcp_client.py"
SHUTDOWN = PROJECT / "Scripts" / "GrokProduction" / "shutdown_blender_mcp.py"

EXPECTED_BLEND = OUTPUT / "M01_Promenade_PropKit_GrokMCP_Production_A.blend"
EXPECTED_GLB = OUTPUT / "exports" / "M01_Promenade_PropKit_GrokMCP_Production_A.glb"
EXPECTED_REPORT = OUTPUT / "grok_implementation_report.json"
EVENTS = ATTEMPT / "grok_events.jsonl"
GROK_STDERR = ATTEMPT / "grok_stderr.log"
GROK_FINAL = ATTEMPT / "grok_final.md"
GROK_EXIT = ATTEMPT / "grok_process_exit.json"
BLENDER_STDOUT = ATTEMPT / "blender_stdout.log"
BLENDER_STDERR = ATTEMPT / "blender_stderr.log"
FINALIZER_STDOUT = ATTEMPT / "finalizer_stdout.log"
FINALIZER_STDERR = ATTEMPT / "finalizer_stderr.log"
PROCESS_SAMPLES = ATTEMPT / "process_tree_samples.jsonl"

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
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_record(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def assert_authority(path: Path, size: int, digest: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"Missing authority: {path}")
    if path.stat().st_size != size:
        raise RuntimeError(f"Authority byte mismatch: {path}")
    if sha256(path) != digest:
        raise RuntimeError(f"Authority SHA-256 mismatch: {path}")


def heavy_processes() -> list[dict]:
    rows = []
    for process in psutil.process_iter(["pid", "name", "create_time"]):
        try:
            if (process.info.get("name") or "").lower() in HEAVY_NAMES:
                rows.append(process.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return rows


def listener_owned_by(pid: int) -> bool:
    try:
        for connection in psutil.net_connections(kind="tcp"):
            if connection.status == psutil.CONN_LISTEN and connection.laddr.port == 9876 and connection.pid == pid:
                return True
    except psutil.AccessDenied:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.settimeout(0.25)
            return probe.connect_ex(("127.0.0.1", 9876)) == 0
    return False


def redact(value: str, secret: str) -> str:
    return value.replace(secret, "[REDACTED]") if secret else value


def sample_process_tree(roots: list[subprocess.Popen], secret: str) -> None:
    rows = []
    visited = set()
    for root in roots:
        if root is None or root.pid in visited:
            continue
        try:
            process = psutil.Process(root.pid)
            candidates = [process] + process.children(recursive=True)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        for candidate in candidates:
            if candidate.pid in visited:
                continue
            visited.add(candidate.pid)
            try:
                rows.append({
                    "pid": candidate.pid,
                    "parent_pid": candidate.ppid(),
                    "name": candidate.name(),
                    "command_line": redact(" ".join(candidate.cmdline()), secret),
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    with PROCESS_SAMPLES.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"at_utc": utc_now(), "processes": rows}) + "\n")


def shutdown_blender(blender_process: subprocess.Popen | None) -> None:
    if blender_process is None or blender_process.poll() is not None:
        return
    try:
        subprocess.run(
            [sys.executable, str(MCP_CLIENT), "--timeout", "30", "execute-file", "--file", str(SHUTDOWN)],
            cwd=str(PROJECT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=45,
            check=False,
        )
    except Exception:
        pass
    deadline = time.monotonic() + 20
    while blender_process.poll() is None and time.monotonic() < deadline:
        time.sleep(0.5)
    if blender_process.poll() is None:
        blender_process.terminate()
        try:
            blender_process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            blender_process.kill()
            blender_process.wait(timeout=8)


def parse_token_usage() -> dict | None:
    if not EVENTS.is_file():
        return None
    usage = None
    for raw_line in EVENTS.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
    return usage


def main() -> int:
    started_at = utc_now()
    blender_process = None
    grok_process = None
    blender_out = None
    blender_err = None
    blender_launches = 0
    grok_launches = 0
    retries = 0
    failure_stage = "preflight"
    failure_message = None
    grok_exit_code = None
    grok_exit_code_type = None
    finalizer_exit_code = None
    finalizer_exit_code_type = None
    timed_out = False
    source_after = None
    secret = ""
    classification = "FAILED_WITH_EVIDENCE"
    sanitized_args = []

    try:
        assert_authority(AUTHORITY, AUTHORITY_BYTES, AUTHORITY_SHA)
        assert_authority(SOURCE, SOURCE_BYTES, SOURCE_SHA)
        for required in (PROMPT, FINALIZER, BLENDER, NODE, CODEX, ROUTER_SECRET_FILE, MCP_CLIENT, SHUTDOWN):
            if not required.is_file():
                raise RuntimeError(f"Required file is absent: {required}")
        if ATTEMPT.exists():
            raise RuntimeError(f"Fresh attempt namespace already exists: {ATTEMPT}")
        active = heavy_processes()
        if active:
            raise RuntimeError(f"Governed heavy process already active: {active}")
        if any(connection.status == psutil.CONN_LISTEN and connection.laddr.port == 9876 for connection in psutil.net_connections(kind="tcp")):
            raise RuntimeError("Port 9876 already has a listener")

        for relative in ("output", "output/scripts", "output/checkpoint", "output/renders", "output/textures", "output/exports", "output/receipts"):
            (ATTEMPT / relative).mkdir(parents=True, exist_ok=False)

        failure_stage = "blender_launch"
        blender_out = BLENDER_STDOUT.open("wb")
        blender_err = BLENDER_STDERR.open("wb")
        blender_process = subprocess.Popen(
            [str(BLENDER), str(SOURCE)],
            cwd=str(PROJECT),
            stdout=blender_out,
            stderr=blender_err,
        )
        blender_launches = 1
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            if blender_process.poll() is not None:
                raise RuntimeError(f"Blender exited before MCP readiness with code {blender_process.returncode}")
            if listener_owned_by(blender_process.pid):
                break
            time.sleep(0.75)
        if not listener_owned_by(blender_process.pid):
            raise RuntimeError("Blender MCP did not bind port 9876 within 120 seconds")

        failure_stage = "grok_launch"
        secret = ROUTER_SECRET_FILE.read_text(encoding="utf-8").strip()
        if len(secret) < 32:
            raise RuntimeError("Router caller capability is invalid")
        base_url = f"http://127.0.0.1:4102/_codex-router/{secret}/v1"
        args = [
            str(NODE), str(CODEX), "exec", "--ephemeral", "--ignore-user-config",
            "--dangerously-bypass-approvals-and-sandbox", "--json", "--color", "never",
            "--output-last-message", str(GROK_FINAL), "-m", "grok-oauth/grok-4.5", "-C", str(PROJECT),
            "-c", 'model_provider="skyguard_router"',
            "-c", 'model_reasoning_effort="high"',
            "-c", 'model_providers.skyguard_router.name="Skyguard Router"',
            "-c", f'model_providers.skyguard_router.base_url="{base_url}"',
            "-c", 'model_providers.skyguard_router.env_key="SKYGUARD_ROUTER_SECRET"',
            "-c", 'model_providers.skyguard_router.wire_api="responses"',
        ]
        sanitized_args = [redact(argument, secret) for argument in args]
        environment = os.environ.copy()
        environment.pop("XAI_API_KEY", None)
        environment["SKYGUARD_ROUTER_SECRET"] = secret
        grok_out = EVENTS.open("wb")
        grok_err = GROK_STDERR.open("wb")
        grok_process = subprocess.Popen(
            args,
            cwd=str(PROJECT),
            env=environment,
            stdin=subprocess.PIPE,
            stdout=grok_out,
            stderr=grok_err,
        )
        grok_launches = 1
        grok_process.stdin.write(PROMPT.read_bytes())
        grok_process.stdin.close()

        failure_stage = "grok_execution"
        deadline = time.monotonic() + 45 * 60
        next_sample = 0.0
        while grok_process.poll() is None:
            now = time.monotonic()
            if now >= next_sample:
                sample_process_tree([blender_process, grok_process], secret)
                next_sample = now + 10
            if now >= deadline:
                timed_out = True
                grok_process.terminate()
                try:
                    grok_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    grok_process.kill()
                    grok_process.wait(timeout=10)
                break
            time.sleep(1)
        grok_process.wait()
        grok_exit_code = int(grok_process.returncode)
        grok_exit_code_type = "System.Int32"
        grok_out.close()
        grok_err.close()

        for path in (EVENTS, GROK_STDERR, GROK_FINAL, PROCESS_SAMPLES):
            if path.is_file():
                path.write_text(redact(path.read_text(encoding="utf-8", errors="replace"), secret), encoding="utf-8")
        write_json(GROK_EXIT, {
            "exit_code": grok_exit_code,
            "exit_code_type": grok_exit_code_type,
            "completed_utc": utc_now(),
            "timed_out": timed_out,
        })
        if timed_out or grok_exit_code != 0:
            raise RuntimeError(f"Grok execution failed or timed out: exit={grok_exit_code}, timed_out={timed_out}")

        failure_stage = "deterministic_finalizer"
        finalizer_out = FINALIZER_STDOUT.open("wb")
        finalizer_err = FINALIZER_STDERR.open("wb")
        finalizer_result = subprocess.run(
            [sys.executable, str(MCP_CLIENT), "--timeout", "1500", "execute-file", "--file", str(FINALIZER)],
            cwd=str(PROJECT),
            stdout=finalizer_out,
            stderr=finalizer_err,
            timeout=1600,
            check=False,
        )
        finalizer_out.close()
        finalizer_err.close()
        finalizer_exit_code = int(finalizer_result.returncode)
        finalizer_exit_code_type = "System.Int32"
        if finalizer_exit_code != 0:
            raise RuntimeError(f"Deterministic finalizer failed with exit code {finalizer_exit_code}")

        failure_stage = "automatic_postflight"
        required_files = [EXPECTED_BLEND, EXPECTED_GLB, EXPECTED_REPORT]
        missing = [str(path) for path in required_files if not path.is_file()]
        if missing:
            raise RuntimeError(f"Missing required final outputs: {missing}")
        report = json.loads(EXPECTED_REPORT.read_text(encoding="utf-8"))
        if report.get("classification") != "PASSED_AWAITING_DIRECT_VISUAL_REVIEW":
            raise RuntimeError("Implementation report did not reach the automatic review boundary")
        renders = sorted((OUTPUT / "renders").glob("*.png"))
        if len(renders) != 8:
            raise RuntimeError(f"Expected exactly eight final renders, found {len(renders)}")
        for render in renders:
            with Image.open(render) as image:
                if image.size != (1920, 1080):
                    raise RuntimeError(f"Wrong render dimensions for {render}: {image.size}")
        source_after = file_record(SOURCE)
        if source_after["bytes"] != SOURCE_BYTES or source_after["sha256"] != SOURCE_SHA:
            raise RuntimeError("Canonical source changed during the governed attempt")
        classification = "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW"
        failure_stage = None
    except Exception as exc:
        failure_message = str(exc)
    finally:
        shutdown_blender(blender_process)
        if blender_out is not None and not blender_out.closed:
            blender_out.close()
        if blender_err is not None and not blender_err.closed:
            blender_err.close()
        if source_after is None and SOURCE.is_file():
            source_after = file_record(SOURCE)
        if ATTEMPT.exists():
            inventory = []
            for path in sorted(path for path in ATTEMPT.rglob("*") if path.is_file() and path != TERMINAL):
                inventory.append(file_record(path))
            terminal = {
                "schema": "skyguard.m01-promenade-prop-kit.grok-mcp.production-attempt01.terminal.v1",
                "created_at_utc": utc_now(),
                "started_at_utc": started_at,
                "classification": classification,
                "failure_stage": failure_stage,
                "failure_message": failure_message,
                "model": "grok-oauth/grok-4.5",
                "provider": "local Codex router authenticated Grok OAuth caller-capability route",
                "xai_api_key_removed_from_child": True,
                "attempt_root": str(ATTEMPT),
                "prompt": file_record(PROMPT),
                "supervisor": file_record(Path(__file__)),
                "finalizer": file_record(FINALIZER),
                "execution": {
                    "blender_launches": blender_launches,
                    "grok_launches": grok_launches,
                    "unreal_launches": 0,
                    "retries": retries,
                    "timed_out": timed_out,
                    "blender_pid": blender_process.pid if blender_process else None,
                    "grok_pid": grok_process.pid if grok_process else None,
                    "grok_exit_code": grok_exit_code,
                    "grok_exit_code_type": grok_exit_code_type,
                    "finalizer_exit_code": finalizer_exit_code,
                    "finalizer_exit_code_type": finalizer_exit_code_type,
                    "token_usage": parse_token_usage(),
                    "sanitized_grok_arguments": sanitized_args,
                },
                "source_authority": {
                    "path": str(SOURCE),
                    "expected_bytes": SOURCE_BYTES,
                    "expected_sha256": SOURCE_SHA,
                    "after": source_after,
                    "unchanged": bool(source_after and source_after["bytes"] == SOURCE_BYTES and source_after["sha256"] == SOURCE_SHA),
                },
                "expected_outputs": {
                    "blend": str(EXPECTED_BLEND),
                    "combined_glb": str(EXPECTED_GLB),
                    "implementation_report": str(EXPECTED_REPORT),
                    "render_count": len(list((OUTPUT / "renders").glob("*.png"))) if (OUTPUT / "renders").exists() else 0,
                },
                "artifacts": inventory,
                "runtime_promotion_performed": False,
                "next_gate": "Independent full-resolution review of all eight original renders and structural receipts." if classification.startswith("PASSED") else "Preserve failure evidence; do not retry this namespace.",
            }
            write_json(TERMINAL, terminal)

    print(classification)
    return 0 if classification == "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
