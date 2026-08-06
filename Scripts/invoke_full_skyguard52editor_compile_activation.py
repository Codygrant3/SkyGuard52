"""Run one evidence-bound full Skyguard52Editor module compile.

This lane never launches Unreal Editor. It records an exhaustive Source
inventory, build logs, a terminal receipt, and—only after a successful build—
an activation record suitable for Phase 4 Attempt07 Recovery03.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE_ROOT = ROOT / "Source"
BUILD_BAT = Path(r"D:\UE_5.8\Engine\Build\BatchFiles\Build.bat")
UPROJECT = ROOT / "Skyguard52.uproject"
MODULE_DLL = ROOT / "Binaries/Win64/UnrealEditor-Skyguard52.dll"
OUTPUT_PARENT = ROOT / "Saved/BuildAttempts/FullModuleCompileActivation"
CONTRACT_ID = "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-03"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def evidence_item(path: Path) -> dict[str, object]:
    return {
        "file": relative(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def source_inventory() -> dict[str, object]:
    files = []
    for path in sorted(item for item in SOURCE_ROOT.rglob("*") if item.is_file()):
        files.append(
            {
                "file": relative(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return {
        "schema": "skyguard.full-module-source-inventory.v1",
        "root": "Source",
        "generated_at_utc": utc_now(),
        "files": files,
    }


def write_json(path: Path, value: object) -> None:
    path.write_bytes(json_bytes(value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--authorize-full-module-compile",
        action="store_true",
        help="Required explicit authorization for the single compile.",
    )
    args = parser.parse_args()
    if not args.authorize_full_module_compile:
        raise RuntimeError("Explicit full-module compile authorization is required")
    if not BUILD_BAT.is_file() or not UPROJECT.is_file() or not SOURCE_ROOT.is_dir():
        raise RuntimeError("Full-module compile prerequisites are missing")

    inventory_before = source_inventory()
    inventory_payload = json_bytes(inventory_before)
    inventory_digest = sha256_bytes(inventory_payload)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    attempt_root = OUTPUT_PARENT / f"attempt_{stamp}_{inventory_digest[:8]}"
    attempt_root.mkdir(parents=True, exist_ok=False)

    inventory_path = attempt_root / "source_inventory.json"
    inventory_path.write_bytes(inventory_payload)
    stdout_path = attempt_root / "build.stdout.log"
    stderr_path = attempt_root / "build.stderr.log"
    receipt_path = attempt_root / "compile_receipt.json"
    activation_path = attempt_root / "compile_activation.json"

    # Both authoritative paths are space-free. Avoid the leading quoted token
    # form here because cmd.exe /s treats it as a literal executable name.
    command_text = (
        f"{BUILD_BAT} Skyguard52Editor Win64 Development "
        f"{UPROJECT} -WaitMutex -NoHotReloadFromIDE"
    )
    command = [
        r"C:\Windows\System32\cmd.exe",
        "/d",
        "/s",
        "/c",
        command_text,
    ]
    started_at = utc_now()
    timed_out = False
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open(
        "w", encoding="utf-8"
    ) as stderr:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=stdout,
            stderr=stderr,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        try:
            exit_code = process.wait(timeout=900)
        except subprocess.TimeoutExpired:
            timed_out = True
            subprocess.run(
                ["taskkill", "/pid", str(process.pid), "/t", "/f"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            exit_code = 124

    inventory_after = source_inventory()
    inventory_after.pop("generated_at_utc", None)
    inventory_comparison = dict(inventory_before)
    inventory_comparison.pop("generated_at_utc", None)
    source_unchanged = inventory_after == inventory_comparison
    module_exists = MODULE_DLL.is_file()
    module_sha = sha256_file(MODULE_DLL) if module_exists else None
    success = exit_code == 0 and not timed_out and source_unchanged and module_exists

    receipt = {
        "schema": "skyguard.full-module-compile-receipt.v1",
        "gate": (
            "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE"
            if success
            else "FAIL_FULL_SKYGUARD52EDITOR_MODULE_COMPILE"
        ),
        "contract_id": CONTRACT_ID,
        "target": "Skyguard52Editor",
        "platform": "Win64",
        "configuration": "Development",
        "started_at_utc": started_at,
        "finished_at_utc": utc_now(),
        "build_exit_code": exit_code,
        "timed_out": timed_out,
        "source_inventory_unchanged": source_unchanged,
        "compiled_module_file": relative(MODULE_DLL) if module_exists else None,
        "compiled_module_bytes": MODULE_DLL.stat().st_size if module_exists else None,
        "compiled_module_sha256": module_sha,
        "command": command,
    }
    write_json(receipt_path, receipt)

    result: dict[str, object] = {
        "attempt_root": str(attempt_root),
        "receipt": str(receipt_path),
        "gate": receipt["gate"],
        "build_exit_code": exit_code,
        "activation": None,
        "activation_sha256": None,
    }
    if success:
        activation = {
            "schema": "skyguard.full-module-compile-activation.v1",
            "contract_id": CONTRACT_ID,
            "gate": "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE",
            "target": "Skyguard52Editor",
            "platform": "Win64",
            "configuration": "Development",
            "build_exit_code": 0,
            "created_at_utc": utc_now(),
            "source_inventory": evidence_item(inventory_path),
            "compile_receipt": evidence_item(receipt_path),
            "build_stdout": evidence_item(stdout_path),
            "build_stderr": evidence_item(stderr_path),
            "compiled_module": evidence_item(MODULE_DLL),
        }
        write_json(activation_path, activation)
        result["activation"] = str(activation_path)
        result["activation_sha256"] = sha256_file(activation_path)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if success else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FULL MODULE COMPILE SUPERVISOR FAILED: {exc}", file=sys.stderr)
        raise
