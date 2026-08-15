#!/usr/bin/env python3
"""Create a non-circular inventory and freeze for this offline toolchain lane."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(r"D:\Skyguard52")
SCRIPT_ROOT = ROOT / "Scripts" / "ToolchainWave08" / "character_audio_environment"
DOC_ROOT = ROOT / "Docs" / "Toolchain" / "ToolchainWave08"
INVENTORY = DOC_ROOT / "character_audio_environment_source_inventory.json"
RESULT = DOC_ROOT / "character_audio_environment_offline_test_result.json"
FREEZE = DOC_ROOT / "character_audio_environment_offline_design_freeze.json"


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: pathlib.Path) -> dict:
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def write_json(path: pathlib.Path, value: object) -> None:
    temporary = pathlib.Path(str(path) + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    verify = subprocess.run(
        [sys.executable, str(SCRIPT_ROOT / "verify_offline.py")],
        text=True,
        capture_output=True,
        check=False,
    )
    unit = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(SCRIPT_ROOT / "tests"), "-p", "test_*.py", "-v"],
        text=True,
        capture_output=True,
        check=False,
    )
    classification = "PASS" if verify.returncode == 0 and unit.returncode == 0 else "FAILED_WITH_EVIDENCE"
    result = {
        "schema": "skyguard.toolchain-wave08.offline-test-result.v1",
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "classification": classification,
        "offline_verifier": {"exit_code": verify.returncode, "stdout": verify.stdout, "stderr": verify.stderr},
        "unit_tests": {"exit_code": unit.returncode, "stdout": unit.stdout, "stderr": unit.stderr},
        "heavy_processes_launched": 0,
        "unreal_launched": False,
        "blender_launched": False,
        "governed_views_created": False,
    }
    write_json(RESULT, result)
    if classification != "PASS":
        return 1

    governed = sorted(
        [path for path in SCRIPT_ROOT.rglob("*") if path.is_file() and "__pycache__" not in path.parts]
        + [
            DOC_ROOT / "character_prototype_contract.json",
            DOC_ROOT / "audio_prototype_contract.json",
            DOC_ROOT / "environment_prototype_contract.json",
            DOC_ROOT / "CHARACTER_AUDIO_ENVIRONMENT_RUNBOOK.md",
            RESULT,
        ],
        key=lambda path: str(path).lower(),
    )
    inventory = {
        "schema": "skyguard.toolchain-wave08.source-inventory.v1",
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "record_count": len(governed),
        "records": [record(path) for path in governed],
        "observed_mutable_manifest": record(ROOT / "Production" / "production_manifest.json"),
        "mutable_manifest_is_not_a_frozen_authority": True,
    }
    write_json(INVENTORY, inventory)

    freeze_members = governed + [INVENTORY]
    freeze = {
        "schema": "skyguard.toolchain-wave08.offline-design-freeze.v1",
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "classification": "PASSED_READY_FOR_THREE_SEPARATE_EXPLICIT_ISOLATED_PREPARATION_AUTHORIZATIONS",
        "scope": ["character", "audio", "environment"],
        "one_heavy_process_policy": True,
        "parallelism_scope": "offline validation only",
        "canonical_project_mutated": False,
        "unreal_launched": False,
        "blender_launched": False,
        "members": [record(path) for path in freeze_members],
        "next_commands": {
            "character": r"powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\ToolchainWave08\character_audio_environment\prepare_character_view_once.ps1 -AuthorizeSinglePrepare",
            "audio": r"powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\ToolchainWave08\character_audio_environment\prepare_audio_view_once.ps1 -AuthorizeSinglePrepare",
            "environment": r"powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\ToolchainWave08\character_audio_environment\prepare_environment_view_once.ps1 -AuthorizeSinglePrepare",
        },
    }
    write_json(FREEZE, freeze)
    print(json.dumps({"classification": freeze["classification"], "freeze": str(FREEZE), "sha256": sha256(FREEZE)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
