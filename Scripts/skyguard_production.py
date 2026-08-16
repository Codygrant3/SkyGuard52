from __future__ import annotations

import argparse
import csv
import ctypes
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from skyguard_visual_feedback import (  # noqa: E402
    FeedbackError,
    evaluate_strategy,
    load_memory as load_visual_feedback_memory,
)

PRODUCTION = ROOT / "Production"
MANIFEST_PATH = PRODUCTION / "production_manifest.json"
ATTEMPTS_ROOT = PRODUCTION / "Attempts"
LOCK_PATH = PRODUCTION / ".heavy_process.lock"
EVENTS_PATH = PRODUCTION / "events.jsonl"
VISUAL_FEEDBACK_MEMORY_PATH = PRODUCTION / "visual_feedback_memory.json"

HEAVY_PROCESS_NAMES = {
    "blender",
    "unrealeditor",
    "unrealeditor-cmd",
    "shadercompileworker",
    "automationtool",
    "unrealbuildtool",
    "cl",
    "link",
}

STATE_TRANSITIONS = {
    "queued": {"ready", "blocked_reference", "deferred"},
    "blocked_reference": {"queued", "ready", "deferred"},
    "source_candidate": {"ready", "blocked_reference", "deferred"},
    "provisional_blockout": {"ready", "blocked_reference", "deferred"},
    "ready": {"running", "blocked_reference", "deferred"},
    "running": {"awaiting_review", "failed"},
    "awaiting_review": {"accepted", "failed"},
    "accepted": set(),
    "failed": {"ready", "deferred"},
    "deferred": {"queued", "ready", "blocked_reference"},
}


class PipelineError(RuntimeError):
    pass


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PipelineError(f"Missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PipelineError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PipelineError(f"JSON root must be an object: {path}")
    return payload


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def append_event(event: dict[str, Any]) -> None:
    PRODUCTION.mkdir(parents=True, exist_ok=True)
    record = {"at_utc": now_utc(), **event}
    with EVENTS_PATH.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, separators=(",", ":")) + "\n")


def load_manifest() -> dict[str, Any]:
    return load_json(MANIFEST_PATH)


def save_manifest(manifest: dict[str, Any]) -> None:
    manifest["project"]["updated_at_utc"] = now_utc()
    atomic_write_json(MANIFEST_PATH, manifest)


def asset_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {asset["id"]: asset for asset in manifest["assets"]}


DEFAULT_NEXT_STATES = (
    "ready,provisional_blockout,source_candidate,queued,blocked_reference"
)


def select_next_assets(
    manifest: dict[str, Any],
    states: set[str],
    limit: int,
) -> list[dict[str, Any]]:
    """Return the next executable assets.

    Deferred, failed, accepted, running, and awaiting_review are skipped unless
    the caller includes those states. Execution-order lanes are applied first so
    the live Apache CPG P0 slice outranks later mission kits even when a later
    lane still has a low numeric priority.
    """
    order = {
        lane: index for index, lane in enumerate(manifest.get("execution_order", []))
    }
    fallback = len(order)
    return sorted(
        (asset for asset in manifest["assets"] if asset["status"] in states),
        key=lambda item: (
            order.get(item.get("lane"), fallback),
            item["priority"],
            item["id"],
        ),
    )[:limit]


def visual_feedback_guard_errors(
    asset: dict[str, Any],
    memory_path: Path = VISUAL_FEEDBACK_MEMORY_PATH,
) -> list[str]:
    if asset.get("feedback_guard_required") is not True:
        return []
    lane = asset.get("feedback_lane")
    tags = asset.get("strategy_tags")
    if not isinstance(lane, str) or not lane:
        return [f"{asset.get('id')}: feedback_lane is required by its feedback guard."]
    if not isinstance(tags, list) or not all(isinstance(tag, str) and tag for tag in tags):
        return [f"{asset.get('id')}: strategy_tags must be a nonempty string list."]
    if not memory_path.is_file():
        return [f"{asset.get('id')}: visual-feedback memory is missing: {memory_path}"]
    try:
        result = evaluate_strategy(load_visual_feedback_memory(memory_path), lane, tags)
    except FeedbackError as exc:
        return [f"{asset.get('id')}: invalid visual-feedback memory: {exc}"]
    if result["pass"]:
        return []
    detail = {
        "missing_required_tags": result.get("missing_required_tags", []),
        "present_forbidden_tags": result.get("present_forbidden_tags", []),
    }
    return [
        f"{asset.get('id')}: strategy blocked by durable visual feedback: "
        + json.dumps(detail, sort_keys=True)
    ]


def validate_manifest(manifest: dict[str, Any], check_files: bool = True) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema") != "skyguard.production-manifest.v1":
        errors.append("Unexpected or missing manifest schema.")
    project = manifest.get("project", {})
    if project.get("root") != str(ROOT):
        errors.append(f"Manifest root {project.get('root')!r} does not equal {ROOT}.")

    policies = manifest.get("policies", {})
    if policies.get("standing_blender_unreal_authorization") is not True:
        errors.append("Standing Blender/Unreal authorization must be enabled.")
    if policies.get("per_run_user_authorization_required") is not False:
        errors.append("Per-run Blender/Unreal user authorization must be disabled.")
    authority_value = policies.get("standing_authorization_authority")
    if not isinstance(authority_value, str) or not authority_value:
        errors.append("Standing-authorization authority path is missing.")
    elif check_files:
        authority_path = ROOT / authority_value
        if not authority_path.is_file():
            errors.append(f"Standing-authorization authority is missing: {authority_path}")
        else:
            try:
                authority = load_json(authority_path)
            except PipelineError as exc:
                errors.append(str(exc))
            else:
                execution_policy = authority.get("execution_policy", {})
                required_authority_values = {
                    "status": "ACTIVE",
                    "canonical_project_root": str(ROOT),
                }
                for key, expected in required_authority_values.items():
                    if authority.get(key) != expected:
                        errors.append(
                            f"Standing-authorization authority mismatch: {key}."
                        )
                required_execution_values = {
                    "per_run_user_authorization_required": False,
                    "one_heavy_process_at_a_time": True,
                    "automatic_retry_count": 0,
                    "failed_namespace_reuse": False,
                    "immutable_attempt_evidence_required": True,
                }
                for key, expected in required_execution_values.items():
                    if execution_policy.get(key) != expected:
                        errors.append(
                            f"Standing-authorization execution-policy mismatch: {key}."
                        )

    allowed = set(policies.get("accepted_states", []))
    ids: list[str] = []
    for position, asset in enumerate(manifest.get("assets", [])):
        asset_id = asset.get("id")
        if not asset_id:
            errors.append(f"Asset at index {position} has no id.")
            continue
        ids.append(asset_id)
        if asset.get("status") not in allowed:
            errors.append(f"{asset_id}: invalid status {asset.get('status')!r}.")
        if not isinstance(asset.get("priority"), int):
            errors.append(f"{asset_id}: priority must be an integer.")
        worker = asset.get("worker")
        if worker:
            script = ROOT / worker.get("script", "")
            if check_files and not script.is_file():
                errors.append(f"{asset_id}: worker script is missing: {script}")
            if not isinstance(worker.get("arguments"), list):
                errors.append(f"{asset_id}: worker arguments must be a list.")
        if check_files:
            errors.extend(visual_feedback_guard_errors(asset))

    duplicates = sorted(asset_id for asset_id, count in Counter(ids).items() if count > 1)
    if duplicates:
        errors.append(f"Duplicate asset ids: {duplicates}")

    for tool_name, authority in manifest.get("toolchain", {}).items():
        path = Path(authority.get("path", ""))
        if check_files and not path.is_file():
            errors.append(f"Missing {tool_name}: {path}")
            continue
        if check_files and authority.get("bytes") != path.stat().st_size:
            errors.append(f"{tool_name}: byte-count mismatch.")
        if check_files and authority.get("sha256") != sha256(path):
            errors.append(f"{tool_name}: SHA-256 mismatch.")
    return errors


def tasklist() -> list[dict[str, str]]:
    completed = subprocess.run(
        ["tasklist.exe", "/fo", "csv", "/nh"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise PipelineError(f"tasklist failed: {completed.stderr.strip()}")
    rows = []
    for row in csv.reader(completed.stdout.splitlines()):
        if len(row) >= 2:
            rows.append({"name": Path(row[0]).stem.lower(), "pid": row[1]})
    return rows


def heavy_processes() -> list[dict[str, str]]:
    return [row for row in tasklist() if row["name"] in HEAVY_PROCESS_NAMES]


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_physical", ctypes.c_ulonglong),
        ("available_physical", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("available_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("available_virtual", ctypes.c_ulonglong),
        ("available_extended_virtual", ctypes.c_ulonglong),
    ]


def free_memory_gb() -> float:
    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise PipelineError("GlobalMemoryStatusEx failed.")
    return status.available_physical / (1024**3)


def process_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def lock_state() -> dict[str, Any] | None:
    if not LOCK_PATH.is_file():
        return None
    try:
        return load_json(LOCK_PATH)
    except PipelineError:
        return {"invalid": True, "path": str(LOCK_PATH)}


def acquire_lock(asset_id: str, attempt_id: str) -> None:
    PRODUCTION.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "skyguard.heavy-process-lock.v1",
        "owner_pid": os.getpid(),
        "asset_id": asset_id,
        "attempt_id": attempt_id,
        "created_at_utc": now_utc(),
    }
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(LOCK_PATH, flags)
    except FileExistsError as exc:
        raise PipelineError(f"Heavy-process lock already exists: {LOCK_PATH}") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2)
        stream.write("\n")


def release_lock() -> None:
    if not LOCK_PATH.exists():
        return
    state = lock_state() or {}
    if state.get("owner_pid") not in (None, os.getpid()):
        raise PipelineError("Refusing to release a lock owned by another process.")
    LOCK_PATH.unlink()


def preflight(manifest: dict[str, Any]) -> dict[str, Any]:
    errors = validate_manifest(manifest)
    active = heavy_processes()
    free_disk = shutil.disk_usage(ROOT).free / (1024**3)
    free_memory = free_memory_gb()
    lock = lock_state()
    if active:
        errors.append(f"Heavy processes are active: {active}")
    if lock:
        errors.append(f"Heavy-process lock exists: {lock}")
    minimum_disk = float(manifest["policies"]["minimum_free_disk_gb"])
    minimum_memory = float(manifest["policies"]["minimum_free_memory_gb"])
    if free_disk < minimum_disk:
        errors.append(f"Free disk {free_disk:.1f} GB is below {minimum_disk:.1f} GB.")
    if free_memory < minimum_memory:
        errors.append(f"Free memory {free_memory:.1f} GB is below {minimum_memory:.1f} GB.")
    return {
        "schema": "skyguard.production-preflight.v1",
        "at_utc": now_utc(),
        "pass": not errors,
        "errors": errors,
        "heavy_processes": active,
        "lock": lock,
        "free_disk_gb": round(free_disk, 2),
        "free_memory_gb": round(free_memory, 2),
    }


def transition(asset: dict[str, Any], new_state: str, reason: str) -> None:
    old_state = asset["status"]
    if new_state not in STATE_TRANSITIONS.get(old_state, set()):
        raise PipelineError(f"Invalid state transition for {asset['id']}: {old_state} -> {new_state}")
    asset["status"] = new_state
    asset["state_reason"] = reason
    asset["state_changed_at_utc"] = now_utc()


def inventory_files(root: Path) -> list[dict[str, Any]]:
    records = []
    if not root.exists():
        return records
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        records.append(
            {
                "relative_path": str(path.relative_to(root)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return records


def output_checks(output_dir: Path, worker: dict[str, Any]) -> tuple[bool, list[str]]:
    errors = []
    blends = list(output_dir.rglob("*.blend")) if output_dir.exists() else []
    glbs = list(output_dir.rglob("*.glb")) if output_dir.exists() else []
    renders = list(output_dir.rglob("*.png")) if output_dir.exists() else []
    minimum_renders = int(worker.get("minimum_renders", 5))
    if len(blends) != 1:
        errors.append(f"Expected exactly one .blend, found {len(blends)}.")
    if len(glbs) != 1:
        errors.append(f"Expected exactly one .glb, found {len(glbs)}.")
    if len(renders) < minimum_renders:
        errors.append(f"Expected at least {minimum_renders} PNG renders, found {len(renders)}.")
    for path in blends + glbs + renders:
        if path.stat().st_size <= 0:
            errors.append(f"Empty output: {path}")
    return not errors, errors


def command_audit(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    errors = validate_manifest(manifest)
    counts = Counter(asset["status"] for asset in manifest["assets"])
    lanes = Counter(asset["lane"] for asset in manifest["assets"])
    workers = [asset["id"] for asset in manifest["assets"] if asset.get("worker")]
    payload = {
        "schema": "skyguard.production-audit.v1",
        "at_utc": now_utc(),
        "pass": not errors,
        "errors": errors,
        "asset_count": len(manifest["assets"]),
        "status_counts": dict(sorted(counts.items())),
        "lane_counts": dict(sorted(lanes.items())),
        "executable_worker_assets": workers,
        "heavy_processes": heavy_processes(),
        "lock": lock_state(),
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["pass"] else 2


def command_next(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    errors = validate_manifest(manifest)
    if errors:
        raise PipelineError("; ".join(errors))
    states = set(args.states.split(","))
    assets = select_next_assets(manifest, states, args.limit)
    print(
        json.dumps(
            [
                {
                    "id": asset["id"],
                    "priority": asset["priority"],
                    "status": asset["status"],
                    "lane": asset["lane"],
                    "name": asset["name"],
                    "has_worker": bool(asset.get("worker")),
                    "blocker": asset.get("blocker"),
                }
                for asset in assets
            ],
            indent=2,
        )
    )
    return 0


def command_preflight(args: argparse.Namespace) -> int:
    result = preflight(load_manifest())
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 3


def command_set_state(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    errors = validate_manifest(manifest)
    if errors:
        raise PipelineError("; ".join(errors))
    asset = asset_index(manifest).get(args.asset)
    if not asset:
        raise PipelineError(f"Unknown asset: {args.asset}")
    transition(asset, args.state, args.reason)
    save_manifest(manifest)
    append_event(
        {
            "event": "state_changed",
            "asset_id": args.asset,
            "state": args.state,
            "reason": args.reason,
        }
    )
    print(json.dumps({"asset_id": args.asset, "status": args.state}, indent=2))
    return 0


def command_run(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    errors = validate_manifest(manifest)
    if errors:
        raise PipelineError("; ".join(errors))
    asset = asset_index(manifest).get(args.asset)
    if not asset:
        raise PipelineError(f"Unknown asset: {args.asset}")
    if asset["status"] != "ready":
        raise PipelineError(f"{args.asset} is {asset['status']}, not ready.")
    worker = asset.get("worker")
    if not worker:
        raise PipelineError(f"{args.asset} has no registered Blender worker.")

    check = preflight(manifest)
    if not check["pass"]:
        raise PipelineError("Preflight failed: " + "; ".join(check["errors"]))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    attempt_id = f"attempt_{timestamp}"
    attempt_dir = ATTEMPTS_ROOT / asset["id"] / attempt_id
    output_dir = attempt_dir / "output"
    if attempt_dir.exists():
        raise PipelineError(f"Attempt namespace already exists: {attempt_dir}")

    attempt_dir.mkdir(parents=True)
    output_dir.mkdir()
    atomic_write_json(attempt_dir / "preflight.json", check)
    acquire_lock(asset["id"], attempt_id)
    transition(asset, "running", f"Single Blender attempt {attempt_id} launched.")
    asset["active_attempt"] = str(attempt_dir.relative_to(ROOT))
    save_manifest(manifest)

    blender = Path(manifest["toolchain"]["blender"]["path"])
    worker_script = ROOT / worker["script"]
    worker_arguments = [
        str(value).format(output_dir=str(output_dir), attempt_dir=str(attempt_dir))
        for value in worker["arguments"]
    ]
    command = [
        str(blender),
        "--background",
        "--factory-startup",
        "--python",
        str(worker_script),
        "--",
        *worker_arguments,
    ]
    stdout_path = attempt_dir / "blender.stdout.log"
    stderr_path = attempt_dir / "blender.stderr.log"
    started = now_utc()
    terminal: dict[str, Any] = {
        "schema": "skyguard.production-attempt.v1",
        "asset_id": asset["id"],
        "attempt_id": attempt_id,
        "started_at_utc": started,
        "command": command,
        "launch_count": 0,
        "retry_count": 0,
        "timeout": False,
        "status": "running",
    }
    process: subprocess.Popen[str] | None = None
    exit_code: int | None = None
    failure: str | None = None
    try:
        with stdout_path.open("w", encoding="utf-8", newline="\n") as stdout, stderr_path.open(
            "w", encoding="utf-8", newline="\n"
        ) as stderr:
            process = subprocess.Popen(
                command,
                cwd=attempt_dir,
                stdout=stdout,
                stderr=stderr,
                text=True,
            )
            terminal["launch_count"] = 1
            terminal["pid"] = process.pid
            atomic_write_json(attempt_dir / "launch.json", terminal)
            try:
                exit_code = process.wait(timeout=int(manifest["policies"]["blender_timeout_seconds"]))
            except subprocess.TimeoutExpired:
                terminal["timeout"] = True
                process.terminate()
                try:
                    process.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=20)
                exit_code = process.returncode
                failure = "Blender exceeded the governed timeout."

        terminal["exit_code"] = exit_code
        terminal["exit_code_type"] = type(exit_code).__name__
        if failure is None and exit_code != 0:
            failure = f"Blender returned nonzero exit code {exit_code}."
        outputs_ok, output_errors = output_checks(output_dir, worker)
        if failure is None and not outputs_ok:
            failure = "; ".join(output_errors)
        terminal["output_validation_errors"] = output_errors
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        terminal["ended_at_utc"] = now_utc()
        terminal["artifact_inventory"] = inventory_files(output_dir)
        terminal["failure"] = failure
        terminal["status"] = "failed" if failure else "awaiting_review"
        atomic_write_json(attempt_dir / "terminal.json", terminal)

        manifest = load_manifest()
        asset = asset_index(manifest)[args.asset]
        if asset["status"] == "running":
            transition(
                asset,
                "failed" if failure else "awaiting_review",
                failure or f"Attempt {attempt_id} completed and awaits visual review.",
            )
        asset.pop("active_attempt", None)
        asset["latest_attempt"] = str(attempt_dir.relative_to(ROOT))
        save_manifest(manifest)
        append_event(
            {
                "event": "attempt_terminal",
                "asset_id": args.asset,
                "attempt_id": attempt_id,
                "status": terminal["status"],
                "exit_code": exit_code,
                "failure": failure,
            }
        )
        release_lock()

    print(json.dumps(terminal, indent=2))
    return 0 if not failure else 4


def command_review(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    errors = validate_manifest(manifest)
    if errors:
        raise PipelineError("; ".join(errors))
    asset = asset_index(manifest).get(args.asset)
    if not asset:
        raise PipelineError(f"Unknown asset: {args.asset}")
    if asset["status"] != "awaiting_review":
        raise PipelineError(f"{args.asset} is {asset['status']}, not awaiting_review.")
    attempt = ROOT / asset.get("latest_attempt", "")
    terminal = load_json(attempt / "terminal.json")
    if terminal.get("status") != "awaiting_review":
        raise PipelineError("Latest attempt terminal receipt is not awaiting_review.")
    new_state = "accepted" if args.decision == "accept" else "failed"
    review = {
        "schema": "skyguard.production-visual-review.v1",
        "asset_id": args.asset,
        "attempt_id": terminal["attempt_id"],
        "decision": args.decision,
        "reviewer": args.reviewer,
        "notes": args.notes,
        "reviewed_at_utc": now_utc(),
        "terminal_sha256": sha256(attempt / "terminal.json"),
    }
    atomic_write_json(attempt / "visual_review.json", review)
    transition(asset, new_state, args.notes)
    save_manifest(manifest)
    append_event(
        {
            "event": "visual_review",
            "asset_id": args.asset,
            "decision": args.decision,
            "reviewer": args.reviewer,
        }
    )
    print(json.dumps(review, indent=2))
    return 0


def command_clear_stale_lock(args: argparse.Namespace) -> int:
    state = lock_state()
    if not state:
        print(json.dumps({"cleared": False, "reason": "No lock exists."}, indent=2))
        return 0
    pid = state.get("owner_pid")
    if isinstance(pid, int) and process_exists(pid):
        raise PipelineError(f"Lock owner PID {pid} is still active.")
    if not args.confirm:
        raise PipelineError("Stale lock detected; rerun with --confirm to remove only the stale lock.")
    LOCK_PATH.unlink()
    append_event({"event": "stale_lock_cleared", "prior_lock": state})
    print(json.dumps({"cleared": True, "prior_lock": state}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Skyguard 52 resumable production controller.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="Validate the canonical manifest and summarize production.")
    audit.set_defaults(func=command_audit)

    next_parser = subparsers.add_parser("next", help="Show the next priority assets.")
    next_parser.add_argument("--limit", type=int, default=10)
    next_parser.add_argument(
        "--states",
        default=DEFAULT_NEXT_STATES,
    )
    next_parser.set_defaults(func=command_next)

    preflight_parser = subparsers.add_parser("preflight", help="Validate toolchain, resources, and process state.")
    preflight_parser.set_defaults(func=command_preflight)

    set_state = subparsers.add_parser("set-state", help="Make one explicit governed state transition.")
    set_state.add_argument("asset")
    set_state.add_argument("state", choices=sorted(STATE_TRANSITIONS))
    set_state.add_argument("--reason", required=True)
    set_state.set_defaults(func=command_set_state)

    run = subparsers.add_parser("run", help="Run exactly one registered Blender worker.")
    run.add_argument("asset")
    run.set_defaults(func=command_run)

    review = subparsers.add_parser("review", help="Record the required human visual decision.")
    review.add_argument("asset")
    review.add_argument("--decision", required=True, choices=["accept", "reject"])
    review.add_argument("--reviewer", required=True)
    review.add_argument("--notes", required=True)
    review.set_defaults(func=command_review)

    clear = subparsers.add_parser("clear-stale-lock", help="Remove a lock only when its owner no longer exists.")
    clear.add_argument("--confirm", action="store_true")
    clear.set_defaults(func=command_clear_stale_lock)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except PipelineError as exc:
        print(json.dumps({"error": str(exc), "at_utc": now_utc()}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
