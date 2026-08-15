"""Offline verifier for the corrected Recovery01 Unreal import."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUTHOR = ROOT / r"Scripts\GrokProduction\author_m01_window_recovery06_unrealready01_import01_recovery01.py"
CONTRACT = ROOT / r"Docs\GrokProduction\Wave02\M01_WINDOW_RECOVERY06_UNREALREADY01_REVERSIBLE_UNREAL_IMPORT01_RECOVERY01_CONTRACT.json"


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
    require(AUTHOR.is_file() and CONTRACT.is_file(), "Recovery01 source or contract missing")
    source_text = AUTHOR.read_text(encoding="utf-8")
    compile(source_text, str(AUTHOR), "exec")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["classification"] == "READY_FOR_SINGLE_REVERSIBLE_UNREAL_IMPORT_RECOVERY01", "Contract classification changed")
    require(contract["launch_policy"] == {"heavy_processes": 1, "unreal_launches": 1, "retries": 0}, "Launch policy changed")
    require('rotation.roll = 90.0' in source_text, "Verified Interchange rotation is absent")
    require('pipeline.set_editor_property("scene_name_sub_folder", False)' in source_text, "Short-path pipeline contract changed")
    require('normalize_frame_materials(frame)' in source_text, "Collision-review material cleanup is absent")
    require('add_canonical_sockets(frame, unreal)' in source_text, "Canonical socket creation is absent")
    require("delete_asset" not in source_text and "delete_directory" not in source_text, "Recovery01 contains a destructive asset operation")

    for key in ("source", "accepted_visual_freeze", "failed_attempt_freeze", "pipeline_probe", "project"):
        authority = contract[key]
        path = Path(authority["path"])
        require(path.is_file(), f"Authority missing: {key}")
        require(path.stat().st_size == authority["bytes"], f"Authority bytes changed: {key}")
        require(sha256(path) == authority["sha256"], f"Authority hash changed: {key}")

    spec = importlib.util.spec_from_file_location("window_import_recovery01", AUTHOR)
    require(spec is not None and spec.loader is not None, "Cannot load Recovery01 author")
    module = importlib.util.module_from_spec(spec)
    original_argv = sys.argv[:]
    try:
        sys.argv = [str(AUTHOR), "--offline-contract-test"]
        try:
            spec.loader.exec_module(module)
        except SystemExit as exc:
            require(exc.code == 0, f"Author offline contract returned {exc.code}")
    finally:
        sys.argv = original_argv

    require(not Path(contract["destination_disk"]).exists(), "Fresh Recovery01 destination exists")
    require(not Path(contract["attempt"]).exists(), "Fresh Recovery01 attempt exists")
    require(not Path(contract["terminal_manifest"]).exists(), "Fresh Recovery01 terminal exists")
    print("PASS_M01_WINDOW_REVERSIBLE_UNREAL_IMPORT01_RECOVERY01_OFFLINE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
