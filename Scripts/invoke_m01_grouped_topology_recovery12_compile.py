"""Run the one authorized Recovery12 full-module compile."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / "Source"
BUILD_BAT = Path(r"D:\UE_5.8\Engine\Build\BatchFiles\Build.bat")
UPROJECT = ROOT / "Skyguard52.uproject"
MODULE = ROOT / "Binaries/Win64/UnrealEditor-Skyguard52.dll"
OUTPUT = ROOT / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY12_COMPILE"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory() -> dict[str, object]:
    return {
        "schema": "skyguard.recovery12.compile-source-inventory.v1",
        "files": [
            {
                "file": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(item for item in SOURCE.rglob("*") if item.is_file())
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorize-single-recovery12-compile", action="store_true")
    args = parser.parse_args()
    if not args.authorize_single_recovery12_compile:
        raise RuntimeError("Explicit Recovery12 compile authorization is required")
    if OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise RuntimeError("Recovery12 compile namespace is already used; retry forbidden")
    if not BUILD_BAT.is_file() or not UPROJECT.is_file():
        raise RuntimeError("Unreal build prerequisites are missing")

    before = inventory()
    payload = (json.dumps(before, indent=2, sort_keys=True) + "\n").encode()
    digest = hashlib.sha256(payload).hexdigest()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    attempt = OUTPUT / f"attempt_{stamp}_{digest[:8]}"
    attempt.mkdir(parents=True)
    inventory_path = attempt / "source_inventory.json"
    inventory_path.write_bytes(payload)
    stdout_path = attempt / "build.stdout.log"
    stderr_path = attempt / "build.stderr.log"
    receipt_path = attempt / "compile_receipt.json"

    command_text = f"{BUILD_BAT} Skyguard52Editor Win64 Development {UPROJECT} -WaitMutex -NoHotReloadFromIDE"
    command = [r"C:\Windows\System32\cmd.exe", "/d", "/s", "/c", command_text]
    started = now()
    timed_out = False
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            exit_code = process.wait(timeout=900)
        except subprocess.TimeoutExpired:
            timed_out = True
            subprocess.run(["taskkill", "/pid", str(process.pid), "/t", "/f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            exit_code = 124

    unchanged = inventory() == before
    success = exit_code == 0 and not timed_out and unchanged and MODULE.is_file()
    receipt = {
        "schema": "skyguard.m01.grouped-topology.recovery12-compile-receipt.v1",
        "contract_id": "P3-M01-GROUPED-TOPOLOGY-MAPPED-ATTEMPT03-RECOVERY12",
        "gate": "PASS_RECOVERY12_FULL_MODULE_COMPILE" if success else "FAIL_RECOVERY12_FULL_MODULE_COMPILE",
        "started_at_utc": started,
        "finished_at_utc": now(),
        "build_exit_code": exit_code,
        "timed_out": timed_out,
        "source_inventory_unchanged": unchanged,
        "source_inventory_sha256": sha256(inventory_path),
        "stdout_sha256": sha256(stdout_path),
        "stderr_sha256": sha256(stderr_path),
        "compiled_module": {
            "path": MODULE.relative_to(ROOT).as_posix(),
            "bytes": MODULE.stat().st_size,
            "sha256": sha256(MODULE),
        } if success else None,
        "automatic_retry_forbidden": True,
        "command": command,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"attempt_root": str(attempt), "receipt": str(receipt_path), **receipt}, indent=2, sort_keys=True))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
