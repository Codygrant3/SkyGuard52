"""Run the one authorized Recovery11 Skyguard52Editor compile and freeze evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE_ROOT = ROOT / "Source"
BUILD_BAT = Path(r"D:\UE_5.8\Engine\Build\BatchFiles\Build.bat")
UPROJECT = ROOT / "Skyguard52.uproject"
MODULE_DLL = ROOT / "Binaries/Win64/UnrealEditor-Skyguard52.dll"
OUTPUT_PARENT = ROOT / "Saved/BuildAttempts/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY11_COMPILE"
CONTRACT_ID = "P3-M01-GROUPED-TOPOLOGY-MAPPED-ATTEMPT03-RECOVERY11"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_inventory() -> dict[str, object]:
    files = []
    for path in sorted(item for item in SOURCE_ROOT.rglob("*") if item.is_file()):
        files.append({
            "file": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return {"schema": "skyguard.recovery11.source-inventory.v1", "files": files}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorize-single-recovery11-compile", action="store_true")
    args = parser.parse_args()
    if not args.authorize_single_recovery11_compile:
        raise RuntimeError("Explicit Recovery11 compile authorization is required")
    if OUTPUT_PARENT.exists() and any(OUTPUT_PARENT.iterdir()):
        raise RuntimeError("Recovery11 compile namespace already contains an attempt; automatic retry is forbidden")
    if not BUILD_BAT.is_file() or not UPROJECT.is_file():
        raise RuntimeError("Unreal build prerequisites are missing")

    inventory_before = source_inventory()
    inventory_bytes = (json.dumps(inventory_before, indent=2, sort_keys=True) + "\n").encode("utf-8")
    inventory_sha = hashlib.sha256(inventory_bytes).hexdigest()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    attempt = OUTPUT_PARENT / f"attempt_{stamp}_{inventory_sha[:8]}"
    attempt.mkdir(parents=True, exist_ok=False)
    inventory_path = attempt / "source_inventory.json"
    inventory_path.write_bytes(inventory_bytes)
    stdout_path = attempt / "build.stdout.log"
    stderr_path = attempt / "build.stderr.log"
    receipt_path = attempt / "compile_receipt.json"

    command_text = f"{BUILD_BAT} Skyguard52Editor Win64 Development {UPROJECT} -WaitMutex -NoHotReloadFromIDE"
    command = [r"C:\Windows\System32\cmd.exe", "/d", "/s", "/c", command_text]
    started = utc_now()
    timed_out = False
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            exit_code = process.wait(timeout=900)
        except subprocess.TimeoutExpired:
            timed_out = True
            subprocess.run(["taskkill", "/pid", str(process.pid), "/t", "/f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            exit_code = 124

    source_unchanged = source_inventory() == inventory_before
    module_exists = MODULE_DLL.is_file()
    success = exit_code == 0 and not timed_out and source_unchanged and module_exists
    receipt = {
        "schema": "skyguard.m01.recovery11.compile-receipt.v1",
        "contract_id": CONTRACT_ID,
        "gate": "PASS_RECOVERY11_FULL_MODULE_COMPILE" if success else "FAIL_RECOVERY11_FULL_MODULE_COMPILE",
        "started_at_utc": started,
        "finished_at_utc": utc_now(),
        "build_exit_code": exit_code,
        "timed_out": timed_out,
        "source_inventory_unchanged": source_unchanged,
        "source_inventory_sha256": sha256_file(inventory_path),
        "stdout_sha256": sha256_file(stdout_path),
        "stderr_sha256": sha256_file(stderr_path),
        "compiled_module": {
            "path": MODULE_DLL.relative_to(ROOT).as_posix(),
            "bytes": MODULE_DLL.stat().st_size,
            "sha256": sha256_file(MODULE_DLL),
        } if module_exists else None,
        "automatic_retry_forbidden": True,
        "command": command,
    }
    write_json(receipt_path, receipt)
    print(json.dumps({"attempt_root": str(attempt), "receipt": str(receipt_path), **receipt}, indent=2, sort_keys=True))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
