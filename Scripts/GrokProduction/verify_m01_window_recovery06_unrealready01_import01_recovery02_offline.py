"""Offline verifier for the fresh Recovery02 reversible Unreal import."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUTHOR = ROOT / r"Scripts\GrokProduction\author_m01_window_recovery06_unrealready01_import01_recovery02.py"
BASE = ROOT / r"Scripts\GrokProduction\author_m01_window_recovery06_unrealready01_import01_recovery01.py"
CONTRACT = ROOT / r"Docs\GrokProduction\Wave02\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY02_CONTRACT.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    require(AUTHOR.is_file() and BASE.is_file() and CONTRACT.is_file(), "Recovery02 source set is incomplete")
    author_text = AUTHOR.read_text(encoding="utf-8")
    compile(author_text, str(AUTHOR), "exec")
    require(sha256(BASE) == "1bbc40d6c0063a60e26be1921698ec43aa18d522a520fb6e5e75532d602e6d79", "Frozen Recovery01 author changed")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["classification"] == "READY_FOR_SINGLE_REVERSIBLE_UNREAL_IMPORT_RECOVERY02", "Contract classification changed")
    require(contract["author"]["bytes"] == AUTHOR.stat().st_size and contract["author"]["sha256"] == sha256(AUTHOR), "Author record changed")
    require(contract["destination"] == "/Game/T08/GW02", "Recovery02 package path changed")
    require(contract["interchange_pipeline"]["import_offset_rotation_roll_degrees"] == -90.0, "Recovery02 roll changed")
    require(contract["launch_policy"] == {"heavy_processes": 1, "unreal_launches": 1, "retries": 0}, "Launch policy changed")

    required_fragments = (
        'source.replace("rotation.roll = 90.0", "rotation.roll = -90.0")',
        'source.count(old_post_edit) != 2',
        'source.replace(old_post_edit, "    save_loaded_asset(frame, unreal)")',
        'DESTINATION = "/Game/T08/GW02"',
        'validate_origin(name, vector(mesh.get_bounds().origin))',
    )
    for fragment in required_fragments:
        require(fragment in author_text, f"Recovery02 correction missing: {fragment}")
    require("delete_asset" not in author_text and "delete_directory" not in author_text, "Recovery02 contains destructive asset operations")

    for key in ("source", "accepted_visual_freeze", "prior_recovery01_freeze", "accepted_pipeline_probe", "failed_probe02_freeze", "project"):
        authority = contract[key]
        path = Path(authority["path"])
        require(path.is_file(), f"Authority missing: {key}")
        require(path.stat().st_size == authority["bytes"], f"Authority bytes changed: {key}")
        require(sha256(path) == authority["sha256"], f"Authority hash changed: {key}")

    completed = subprocess.run(
        [sys.executable, str(AUTHOR), "--offline-contract-test"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    require(completed.returncode == 0, f"Author offline contract failed: {completed.stderr}")
    require("PASS_M01_WINDOW_REVERSIBLE_UNREAL_IMPORT01_RECOVERY02_CONTRACT" in completed.stdout, "Author offline PASS token missing")
    require(not Path(contract["destination_disk"]).exists(), "Fresh Recovery02 destination exists")
    require(not Path(contract["attempt"]).exists(), "Fresh Recovery02 attempt exists")
    require(not Path(contract["terminal_manifest"]).exists(), "Fresh Recovery02 terminal exists")
    print("PASS_M01_WINDOW_REVERSIBLE_UNREAL_IMPORT01_RECOVERY02_OFFLINE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
